from django.utils import timezone
from decimal import Decimal

from django.db import models

from config.models import BaseModel


class BookingStatus(models.TextChoices):
    CONFIRMED = 'confirmed', 'Подтверждена'
    COMPLETED = 'completed', 'Выполнена'
    CANCELLED = 'cancelled', 'Отменена'
    NO_SHOW = 'no_show', 'Не явился'
    RESCHEDULED = 'rescheduled', 'Перенесена'

class Bookings(BaseModel):
    status = models.CharField(
        choices=BookingStatus,
        default=BookingStatus.CONFIRMED,
        verbose_name="Статус"
    )
    client = models.ForeignKey(
        to = "account.Clients",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Клиент"
    )
    employee = models.ForeignKey(
        to = "account.Employees",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Мастер"
    )
    service = models.ForeignKey(
        to = "Services",
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Услуга"
    )
    booking_date = models.DateTimeField(
        verbose_name="Дата записи"
    )
    start_time = models.TimeField(
        verbose_name="Время начала"
    )
    end_time = models.TimeField(
        verbose_name="Время окончания"
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


    objects = models.Manager()

    class Meta:
        ordering = ('-created_at', )
        db_table = 'bookings'
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        indexes = [
            models.Index(fields=['client_id', 'booking_date']),
            models.Index(fields=['employee_id', 'booking_date']),
            models.Index(fields=['status', 'booking_date']),
        ]

    def __str__(self):
        return f"Запись {self.client.full_name} - {self.booking_date} {self.start_time}"

    def cancel(self, reason=None):
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Запись уже отменена")

        if self.status == BookingStatus.COMPLETED:
            raise ValueError("Завершенную запись нельзя отменить")

        self.status = BookingStatus.CANCELLED
        self.cancelled_at = timezone.now()

        if reason:
            self.cancellation_reason = reason

        self.save()

    def mark_no_show(self):
        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Запись отменена")
        if self.status == BookingStatus.RESCHEDULED:
            raise ValueError("Запись перенесена")
        if self.status == BookingStatus.NO_SHOW:
            raise ValueError("Запись уже отмечена как неявка")
        from datetime import datetime
        booking_datetime = datetime.combine(self.booking_date, self.start_time)
        if booking_datetime > timezone.now():
            raise ValueError("Неявку можно поставить только после начала записи")
        self.status = BookingStatus.NO_SHOW
        self.save()

    def reschedule(self, new_date, new_start_time, new_end_time):

        if self.status == BookingStatus.CANCELLED:
            raise ValueError("Отмененную запись нельзя перенести")

        if self.status == BookingStatus.COMPLETED:
            raise ValueError("Завершенную запись нельзя перенести")

        if self.status == BookingStatus.RESCHEDULED:
            raise ValueError("Запись уже была перенесена")

        if self.status == BookingStatus.NO_SHOW:
            raise ValueError("Неявку нельзя перенести")

        new_booking = Bookings.objects.create(
            client=self.client,
            employee=self.employee,
            service=self.service,
            booking_date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            total_price=self.total_price,
            discount_amount=self.discount_amount,
            final_price=self.final_price,
            client_notes=self.client_notes,
            status=BookingStatus.CONFIRMED,
            rescheduled_from=self,
        )

        self.status = BookingStatus.RESCHEDULED
        self.save()

        return new_booking