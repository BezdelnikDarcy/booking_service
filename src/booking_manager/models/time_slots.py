from django.db import models
from django.core.exceptions import ValidationError
from config.models import BaseModel


class TimeSlots(BaseModel):

    employee = models.ForeignKey(
        to='account.Employees',
        on_delete=models.CASCADE,
        related_name='time_slots',
        verbose_name='Мастер'
    )

    date = models.DateField(
        verbose_name='Дата'
    )
    start_time = models.TimeField(
        verbose_name='Время начала'
    )
    end_time = models.TimeField(
        verbose_name='Время окончания'
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name='Свободно'
    )

    booking = models.ForeignKey(
        to='Bookings',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_slot',
        verbose_name='Запись'
    )

    class Meta:
        db_table = 'time_slots'
        verbose_name = 'Слот'
        verbose_name_plural = 'Слоты'
        ordering = ('date', 'start_time')
        unique_together = ['master', 'date', 'start_time']

    def __str__(self):
        status = 'свободен' if self.is_available else 'занят'
        return f'{self.master.full_name} — {self.date} {self.start_time} ({status})'

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Время начала не может быть позже времени окончания')

    def occupy(self, booking):
        """Занять слот записью"""
        if not self.is_available:
            raise ValueError('Слот уже занят')
        self.is_available = False
        self.booking = booking
        self.save()

    def free(self):
        """Освободить слот"""
        self.is_available = True
        self.booking = None
        self.save()