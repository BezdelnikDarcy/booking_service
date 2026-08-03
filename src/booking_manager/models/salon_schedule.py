from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from config.models import BaseModel
from django.core.exceptions import ValidationError
from booking_manager.constants import Weekday


class SalonSchedule(BaseModel):
    weekday = models.PositiveSmallIntegerField(
        choices=Weekday,
        verbose_name="День недели"
    )
    start_time = models.TimeField(
        verbose_name="Начало работы"
    )
    end_time = models.TimeField(
        verbose_name="Конец работы"
    )
    is_working = models.BooleanField(
        default=True,
        verbose_name="Открыт"
    )

    class Meta:
        ordering = ('weekday',)
        db_table = 'salon_schedule'
        verbose_name = "График работы салона"
        verbose_name_plural = "График работы салона"

        constraints = [
            models.UniqueConstraint(
                fields=["weekday"],
                name="unique_salon_weekday"
            )
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(
                "Время окончания должно быть позже времени начала"
            )
    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}–{self.end_time}"