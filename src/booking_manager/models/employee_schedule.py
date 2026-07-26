from django.db import models

from config.models import BaseModel
from django.core.exceptions import ValidationError
from booking_manager.constants import Weekday
from booking_manager.models.salon_schedule import SalonSchedule


class EmployeeSchedule(BaseModel):
    employee = models.ForeignKey(
        to="account.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Расписание мастера"
    )
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday,
        verbose_name="День недели"
    )
    start_time = models.TimeField(
        verbose_name="Начало"
    )
    end_time = models.TimeField(
        verbose_name="Конец"
    )
    is_working = models.BooleanField(
        default=True,
        verbose_name="На работе"
    )

    class Meta:
        ordering = ["employee", "weekday"]
        db_table = 'schedule'
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "weekday"],
                name="unique_employee_weekday"
            )
        ]
        indexes = [
            models.Index(fields=["employee", "weekday"])
        ]
    def __str__(self):
        return f'{self.employee} работает {self.get_weekday_display()} с {self.start_time} по {self.end_time}'

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(
                "Время окончания должно быть позже начала"
            )
        try:
            salon_schedule = SalonSchedule.objects.get(weekday=self.weekday)
        except SalonSchedule.DoesNotExist:
            raise ValidationError({
                "weekday": "Сначала настройте график работы салона."
            })
        if not salon_schedule.is_working:
            raise ValidationError({
                'weekday' : f'В {self.get_weekday_display()} салон не работает',
            })
        if self.start_time < salon_schedule.start_time:
            raise ValidationError({
                'start_time': f'Салон открывается в {salon_schedule.start_time}',
            })
        if self.end_time > salon_schedule.end_time:
            raise ValidationError({
                'end_time': f'Салон закрывается {salon_schedule.end_time}',
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
