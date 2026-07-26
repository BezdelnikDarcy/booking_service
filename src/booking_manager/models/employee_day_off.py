from django.db import models
from config.models import BaseModel
from django.core.exceptions import ValidationError
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

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(
                "День начала должна быть не позже даты окончания"
            )
        if EmployeeDayOff.objects.filter(
                employee=self.employee,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
        ).exclude(id=self.id).exists():
            raise ValidationError("У мастера уже есть отпуск на этот период")

        active_bookings = Bookings.objects.filter(
            employee_service__employee=self.employee,
            status=BookingStatus.CONFIRMED,
            start_at__date__range=[self.start_date, self.end_date],
        )
        if active_bookings.exists():
            raise ValidationError(
                f"У мастера есть {active_bookings.count()} активных записей на этот период. "
                f"Сначала перенесите или отмените их."
            )