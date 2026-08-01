from decimal import Decimal
from booking_manager.models.bookings import Bookings
from booking_manager.models.employee_day_off import EmployeeDayOff
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from booking_manager.constants import BookingStatus, ServiceStatus, DiscountType
from booking_manager.models.employee_schedule import EmployeeSchedule
from booking_manager.tasks import(
send_booking_canceled_email_notification,
send_booking_rescheduled_email_notification
)
from booking_manager.models.promocodes import PromoCodes
from booking_manager.models.promo_usage import PromoUsage


class BookingService:


    @staticmethod
    def _validate_booking_not_in_past(start_at):
        if start_at < timezone.now():
            raise ValidationError({
                'start_at': 'Нам ничего не известно о машине времени, измените время',
            })

    @staticmethod
    def _validate_employee_day_off(employee, start_at):
        if EmployeeDayOff.objects.filter(
            employee=employee,
            start_date__lte=start_at.date(),
            end_date__gte=start_at.date(),
        ).exists():
            raise ValidationError({
                'start_at': 'Мастер на выходном',
            })


    @staticmethod
    def _validate_employee_is_available(employee, weekday, start_at, end_at):
        if not EmployeeSchedule.objects.filter(
            employee=employee,
            weekday=weekday,
            is_working=True,
            start_time__lte=start_at.time(),
            end_time__gte=end_at.time(),
        ).exists():
            raise ValidationError({
                'start_at': 'Мастер не работает',
            })

    @staticmethod
    def _validate_employee_service_is_active(employee_service):
        if employee_service.service.status != ServiceStatus.ACTIVE:
            raise ValidationError({
                'employee_service': 'Услуга недоступна',
            })


    @staticmethod
    def _validate_time_conflict_employee(employee, start_at, end_at):
        if Bookings.objects.filter(
            employee_service__employee=employee,
            status=BookingStatus.CONFIRMED,
            start_at__lt=end_at,
            end_at__gt=start_at,
        ).exists():
            raise ValidationError({
                'start_at': 'У мастера уже есть запись на это время',
                'employee_service': 'Выберите другое время или мастера',
            })

    @staticmethod
    def _validate_time_conflict_client(client, start_at, end_at):
        if Bookings.objects.filter(
                client=client,
                status=BookingStatus.CONFIRMED,
                start_at__lt=end_at,
                end_at__gt=start_at,
        ).exists():
            raise ValidationError({
                'start_at': 'На это время у вас уже есть запись',
                'employee_service': 'Выберите другое время',
            })



    @staticmethod
    def _validate_promo_code_is_valid(code):
        if not code.is_valid():
            raise ValidationError(
                "Промокод не действителен"
            )


    @staticmethod
    def calculate_discount(discount_type,discount_value, price):
        if discount_type == DiscountType.PERCENT:
            discount = price * discount_value / 100
        else:
            discount = Decimal(discount_value)

        if price <= discount:
            discount = price
        return discount

    @staticmethod
    def create_booking(client, employee_service, start_at, promo_code = None, **kwargs):
        employee = employee_service.employee
        weekday = start_at.weekday()
        duration = employee_service.duration
        end_at = start_at + timedelta(minutes=duration)
        #Запрет на создание записи в прошлом
        BookingService._validate_booking_not_in_past(start_at)
        #Проверка на выходном ли мастер в этот день
        BookingService._validate_employee_day_off(employee, start_at)
        #Проверка активна ли услуга мастера
        BookingService._validate_employee_service_is_active(employee_service)
        #Проверка работает ли мастер в это время
        BookingService._validate_employee_is_available(employee, weekday, start_at, end_at)
        #Проверка конфликта записи к мастеру на одно и то же время
        BookingService._validate_time_conflict_employee(employee, start_at, end_at)
        #Проверка конфликта записи клиентов на одно и то же время
        BookingService._validate_time_conflict_client(client, start_at, end_at)


        discount = Decimal('0.00')
        with transaction.atomic():
            code = None
            if promo_code:
                try:
                    code = PromoCodes.objects.get(
                        code=promo_code,
                    )
                except PromoCodes.DoesNotExist:
                    raise ValidationError("Промокод не существует")
                #Проверка валиде ли промокод
                BookingService._validate_promo_code_is_valid(code)

                price = employee_service.price
                discount_value = code.discount_value
                discount_type = code.discount_type
                discount = BookingService.calculate_discount(discount_type,discount_value, price)

                code.used_count += 1
                code.save(update_fields=['used_count'])



            booking = Bookings.objects.create(
                client=client,
                employee_service=employee_service,
                start_at=start_at,
                discount_amount=discount,
                **kwargs
            )
            if code is not None:
                PromoUsage.objects.create(
                    promo=code,
                    client=client,
                    booking=booking,
                )
        return booking




    @staticmethod
    def mark_no_show(booking):
        if booking.status != BookingStatus.COMPLETED:
            raise ValidationError("Только завершённую запись можно отметить как неявку")
        booking.status = BookingStatus.NO_SHOW
        booking.save(update_fields=['status'])

    @staticmethod
    def complete_booking(booking):
        if booking.status != BookingStatus.CONFIRMED:
            raise ValidationError(
                "Завершить можно только подтверждённую запись"
            )

        booking.status = BookingStatus.COMPLETED
        booking.save(update_fields=["status"])


    @staticmethod
    def cancel_booking(booking, reason):
        if booking.status != BookingStatus.CONFIRMED:
            raise ValidationError("Отменить можно только подтверждённую запись")

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = timezone.now()

        if reason:
            booking.cancellation_reason = reason

        booking.save(update_fields=[
            'status',
            'cancelled_at',
            'cancellation_reason',
        ])

        send_booking_canceled_email_notification.delay(booking.id)


    @staticmethod
    @transaction.atomic
    def reschedule_booking(booking, new_start_at):
        if booking.status != BookingStatus.CONFIRMED:
            raise ValidationError(
                "Перенести можно только подтверждённую запись"
            )
        if new_start_at < timezone.now():
            raise ValidationError(
                "Нельзя перенести запись в прошлое"
            )
        new_end_at = new_start_at + timedelta(
            minutes=booking.employee_service.duration
        )
        new_booking = BookingService.create_booking(
            client=booking.client,
            employee_service=booking.employee_service,
            start_at=new_start_at,
            end_at=new_end_at,
            total_price=booking.total_price,
            discount_amount=booking.discount_amount,
            final_price=booking.final_price,
            client_notes=booking.client_notes,
            status=BookingStatus.CONFIRMED,
            rescheduled_from=booking,
        )
        booking.status = BookingStatus.RESCHEDULED
        booking.save(update_fields=['status'])
        send_booking_rescheduled_email_notification.delay(new_booking.id)
        return new_booking