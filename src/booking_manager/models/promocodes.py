from decimal import Decimal

from django.db import models
from config.models import BaseModel
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from booking_manager.constants import DiscountType


class PromoCodes(BaseModel):
    code = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Промокод"
    )
    discount_type = models.CharField(
        choices=DiscountType,
        default=DiscountType.PERCENT,
        verbose_name="Тип скидки"
    )
    discount_value = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ],
        verbose_name="Скидка"
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name="Активен"
    )
    valid_from = models.DateTimeField(
        verbose_name="Начало акции"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Окончание акции"
    )
    max_usages = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators= [
            MinValueValidator(1),
        ],
        verbose_name="Колличесво использований"
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество использований"
    )
    only_for_new_clients = models.BooleanField(
        default=False,
        verbose_name="Только для новых клиентов"
    )

    def is_valid(self):
        now = timezone.now()

        if not self.is_active:
            return False

        if now < self.valid_from:
            return False

        if self.valid_until:
            if now > self.valid_until:
                return False
        if self.max_usages:
            if self.used_count >= self.max_usages:
                return False

        return True


    class Meta:
        ordering = ["-created_at"]
        db_table = "promos"
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return f"Промокод {self.code} - {self.is_active}"