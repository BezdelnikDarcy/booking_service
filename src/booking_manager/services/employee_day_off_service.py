from booking_manager.models.bookings import Bookings
from booking_manager.models.employee_day_off import EmployeeDayOff
from django.core.exceptions import ValidationError

from booking_manager.constants import BookingStatus


class EmployeeDayOffService:

    @staticmethod
    def _validate_exist_day_off(employee, start_date, end_date):
        if EmployeeDayOff.objects.filter(
                employee=employee,
                start_date__lte=end_date,
                end_date__gte=start_date,
        ).exists():
            raise ValidationError("У мастера уже есть отпуск на этот период")



    @staticmethod
    def _validate_start_and_end_day_off(start_date, end_date):
        if end_date < start_date:
            raise ValidationError(
                "День начала должна быть не позже даты окончания"
            )

    @staticmethod
    def _validate_employee_has_booking(employee, start_date, end_date):
        active_bookings =  Bookings.objects.filter(
            employee_service__employee=employee,
            status=BookingStatus.CONFIRMED,
            start_at__date__range=[start_date, end_date],
        )
        if active_bookings.exists():
            raise ValidationError(
                f"У мастера есть {active_bookings.count()} активных записей на этот период. "
                f"Сначала перенесите или отмените их."
            )

    @staticmethod
    def _validate_has_reason(reason):
        if not reason:
            raise ValidationError(
                f"Укажите причину выходного"
            )

    @staticmethod
    def create_employee_days_off(employee, start_date, end_date, reason):

        #Проверка дат выходных, выходной должен начаться раньше даты окончания
        EmployeeDayOffService._validate_start_and_end_day_off(start_date, end_date)
        #Проверка причины выходного
        EmployeeDayOffService._validate_has_reason(reason)
        #Проверка на существующий выходной в эти даты
        EmployeeDayOffService._validate_exist_day_off(employee, start_date, end_date)
        #Проверка существуют ли записи к мастеру на выбраные даты
        EmployeeDayOffService._validate_employee_has_booking(employee, start_date, end_date)


        employee_day_off = EmployeeDayOff.objects.create(
            employee=employee,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )
        return employee_day_off