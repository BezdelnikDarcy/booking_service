from booking_manager.models.bookings import Bookings
from booking_manager.models.employee_schedule import EmployeeSchedule
from booking_manager.models.salon_schedule import SalonSchedule
from django.core.exceptions import ValidationError

from booking_manager.constants import BookingStatus




class EmployeeScheduleService:

    @staticmethod
    def get_salon_schedule(weekday):
        try:
            salon_schedule =  SalonSchedule.objects.get(weekday=weekday)
            return salon_schedule
        except SalonSchedule.DoesNotExist:
            return None



    @staticmethod
    def _validate_has_salon_schedule(weekday):
        if not EmployeeScheduleService.get_salon_schedule(weekday):
            raise ValidationError({
                "weekday": "Сначала настройте график работы салона."
            })

    @staticmethod
    def _validate_salon_working(weekday):
        if not EmployeeScheduleService.get_salon_schedule(weekday).is_working:
            raise ValidationError({
                'weekday' : f'Салон не работает в этот день',
            })


    @staticmethod
    def _validate_end_time_schedule(weekday, end_time):
        if end_time > EmployeeScheduleService.get_salon_schedule(weekday).end_time:
            raise ValidationError({
                'end_time': f'Салон закрывается {EmployeeScheduleService.get_salon_schedule(weekday).end_time}',
            })

    @staticmethod
    def _validate_start_time_schedule(weekday, start_time):
        if start_time < EmployeeScheduleService.get_salon_schedule(weekday).start_time:
            raise ValidationError({
                'end_time': f'Салон открывается в {EmployeeScheduleService.get_salon_schedule(weekday).start_time}',
            })




    @staticmethod
    def create_employee_schedule(employee, weekday, start_time, end_time):

        #Проверка существует ли расписание салона
        EmployeeScheduleService._validate_has_salon_schedule(weekday)
        #Проверка работает ли салон в этот день
        EmployeeScheduleService._validate_salon_working(weekday)
        #Проверка на окончание рабочего дня не позже расписания работы салона
        EmployeeScheduleService._validate_end_time_schedule(weekday, end_time)
        #Проверка на начало рабочего дня мастера не раньше расписания работы салона
        EmployeeScheduleService._validate_start_time_schedule(weekday, start_time)


        employee_schedule = EmployeeSchedule.objects.create(
            employee=employee,
            weekday=weekday,
            start_time=start_time,
            end_time=end_time,
        )
        employee_schedule.save()
        return employee_schedule