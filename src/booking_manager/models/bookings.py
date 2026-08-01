from datetime import timedelta
from decimal import Decimal
from django.db import models
from booking_manager.constants import BookingStatus
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
        verbose_name="Клиент",
        limit_choices_to = {'is_active': True},
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

    @property
    def employee(self):
        return self.employee_service.employee

    @property
    def service(self):
        return self.employee_service.service



    def save(self, *args, **kwargs):

        if not self.end_at and self.start_at and self.employee_service:
            duration = self.employee_service.duration
            self.end_at = self.start_at + timedelta(minutes=duration)
        self.total_price = self.employee_service.price
        self.final_price = self.total_price - self.discount_amount
        super().save(*args, **kwargs)