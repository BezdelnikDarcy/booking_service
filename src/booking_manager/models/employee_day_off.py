from django.db import models
from config.models import BaseModel
from booking_manager.models.bookings import Bookings
from booking_manager.constants import BookingStatus


class EmployeeDayOff(BaseModel):
    employee = models.ForeignKey(
        to="account.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="days_off",
        verbose_name="Мастер"
    )
    start_date = models.DateField(
        verbose_name="Начало"
    )

    end_date = models.DateField(
        verbose_name="Окончание"
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Причина"
    )

    class Meta:
        ordering = ["employee", "start_date"]
        db_table = 'day_off'
        verbose_name = 'Не рабочий день'
        verbose_name_plural = 'Не рабочие дни'
        indexes = [
            models.Index(fields=["employee", "start_date", "end_date"]),
        ]

    def __str__(self):
        return f"Не рабочие дни {self.employee} c {self.start_date} по {self.end_date} по причине <{self.reason}>"

