from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from booking_manager.constants import BookingStatus, ServiceStatus
from booking_manager.models.employee_schedule import EmployeeSchedule
# from booking_manager.tasks import(
# send_booking_canceled_email_notification,
# send_booking_rescheduled_email_notification
# )
from config.models import BaseModel


class Bookings(BaseModel):
    status = models.CharField(
        choices=BookingStatus,
        default=BookingStatus.CONFIRMED,
        verbose_name="Статус"
    )
    client = models.ForeignKey(
        to = "account.ClientProfile",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Клиент"
    )
    employee_service = models.ForeignKey(
        to = "EmployeeService",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Услуга мастера"
    )

    promo_code = models.ForeignKey(
    to="PromoCodes",
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="bookings",
    verbose_name="Промокод",
)

    start_at = models.DateTimeField(
        verbose_name="Начало записи"
    )

    end_at = models.DateTimeField(
        verbose_name="Окончание записи",
        null=True,
        blank=True
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Общая стоимость',
        default=Decimal('0.00')
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма скидки',
        default=Decimal('0.00')
    )

    final_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name='Итоговая стоимость'
    )
    client_notes = models.TextField(
        blank=True,
        verbose_name='Пожелания клиента'
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='Причина отмены'
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата отмены'
    )
    rescheduled_from = models.ForeignKey(
        to = 'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rescheduled_to',
        verbose_name='Перенесено из записи'
    )

    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Отправлено напоминание'
    )

    reminder_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата отправки напоминания'
    )



    class Meta:
        ordering = ['-created_at', ]
        db_table = 'bookings'
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        indexes = [
            models.Index(
                fields=['client', 'start_at']
            ),
            models.Index(
                fields=['employee_service', 'start_at']
            ),
            models.Index(
                fields=['status', 'start_at']
            ),
        ]

    def __str__(self):
        return f"Запись {self.client.user.full_name} - {self.service.name} {self.start_at}"

    def cancel(self, reason=None):
        if self.status != BookingStatus.CONFIRMED:
            raise ValidationError("Отменить можно только подтверждённую запись")

        self.status = BookingStatus.CANCELLED
        self.cancelled_at = timezone.now()

        if reason:
            self.cancellation_reason = reason

        self.save(update_fields=[
            'status',
            'cancelled_at',
            'cancellation_reason',
        ])
        from booking_manager.tasks import send_booking_canceled_email_notification
        send_booking_canceled_email_notification.delay(self.id)

    def mark_no_show(self):
        if self.status != BookingStatus.COMPLETED:
            raise ValidationError("Только завершённую запись можно отметить как неявку")
        self.status = BookingStatus.NO_SHOW
        self.save(update_fields=['status'])

    @transaction.atomic
    def reschedule(self, new_start_at):

        if self.status != BookingStatus.CONFIRMED:
            raise ValidationError(
                "Перенести можно только подтверждённую запись"
            )

        if new_start_at < timezone.now():
            raise ValidationError(
                "Нельзя перенести запись в прошлое"
            )
        new_end_at=new_start_at + timedelta(
            minutes=self.employee_service.duration
        )

        new_booking = Bookings.objects.create(
            client=self.client,
            employee_service=self.employee_service,
            start_at=new_start_at,
            end_at=new_end_at,
            total_price=self.total_price,
            discount_amount=self.discount_amount,
            final_price=self.final_price,
            client_notes=self.client_notes,
            status=BookingStatus.CONFIRMED,
            rescheduled_from=self,
        )

        self.status = BookingStatus.RESCHEDULED
        self.save(update_fields=['status'])
        from booking_manager.tasks import send_booking_rescheduled_email_notification
        send_booking_rescheduled_email_notification.delay(new_booking.id)

        return new_booking

    def complete(self):
        if self.status != BookingStatus.CONFIRMED:
            raise ValidationError(
                "Завершить можно только подтверждённую запись"
            )

        self.status = BookingStatus.COMPLETED
        self.save(update_fields=["status"])

    @property
    def employee(self):
        return self.employee_service.employee

    @property
    def service(self):
        return self.employee_service.service

    def clean(self):
        if self.is_available_service():
            raise ValidationError({
                'employee_service': 'Услуга недоступна',
            })
        if not self.start_at or not self.end_at:
            return
        if self.start_at < timezone.now():
            raise ValidationError({
                'start_at': 'Нам ничего не известно о машине времени, измените время',
            })
        if not self.is_employee_available():
            raise ValidationError({
                'start_at': 'Мастер не работает',
            })
        if self.is_employee_day_off():
            raise ValidationError({
                'start_at': 'Мастер на выходном',
            })

        if self.has_time_conflict_master():
            raise ValidationError({
                'start_at': 'У мастера уже есть запись на это время',
                'employee_service': 'Выберите другое время или мастера',
            })
        elif self.has_time_conflict_client():
            raise ValidationError({
                'start_at': 'На это время у вас уже есть запись',
                'employee_service': 'Выберите другое время',
            })

    def is_available_service(self):
        return self.service.status != ServiceStatus.ACTIVE

    def is_employee_day_off(self):
        from booking_manager.models.employee_day_off import EmployeeDayOff
        return EmployeeDayOff.objects.filter(
            employee=self.employee,
            start_date__lte=self.start_at.date(),
            end_date__gte=self.end_at.date(),
        ).exists()

    def is_employee_available(self):
        weekday = self.start_at.weekday()
        return EmployeeSchedule.objects.filter(
            employee=self.employee,
            weekday=weekday,
            is_working=True,
            start_time__lte=self.start_at.time(),
            end_time__gte=self.end_at.time(),
        ).exists()


    def has_time_conflict_master(self):
        if self.start_at is None or self.end_at is None:
            return False

        if self.employee_service is None:
            return False

        return Bookings.objects.filter(
            employee_service__employee=self.employee,
            status=BookingStatus.CONFIRMED,
            start_at__lt=self.end_at,
            end_at__gt=self.start_at,
        ).exclude(
            id=self.id
        ).exists()



    def has_time_conflict_client(self):
        if self.start_at is None or self.end_at is None:
            return False

        if self.employee_service is None:
            return False

        return Bookings.objects.filter(
                client=self.client,
                status=BookingStatus.CONFIRMED,
                start_at__lt=self.end_at,
                end_at__gt=self.start_at,
        ).exclude(id=self.id).exists()



    def save(self, *args, **kwargs):

        if not self.end_at and self.start_at and self.employee_service:
            duration = self.employee_service.duration
            self.end_at = self.start_at + timedelta(minutes=duration)
        self.total_price = self.employee_service.price
        self.final_price = self.total_price - self.discount_amount
        self.full_clean()
        super().save(*args, **kwargs)