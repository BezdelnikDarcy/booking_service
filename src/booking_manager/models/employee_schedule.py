from django.db import models

from config.models import BaseModel
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
