from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from config.models import BaseModel
from booking_manager.managers import ServiceManager


class ServiceStatus(models.TextChoices):
    ACTIVE = 'active', 'Активна'
    INACTIVE = 'inactive', 'Неактивна'
    ARCHIVED = 'archived', 'Архивирована'

class BookingStatus(models.TextChoices):
    CONFIRMED = 'confirmed', 'Подтверждена'
    COMPLETED = 'completed', 'Выполнена'
    CANCELLED = 'cancelled', 'Отменена'
    NO_SHOW = 'no_show', 'Не явился'
    RESCHEDULED = 'rescheduled', 'Перенесена'

class Services(BaseModel):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Наименование"
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Описание"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость"
    )
    status = models.CharField(
        choices=ServiceStatus,
        default=ServiceStatus.INACTIVE,
        verbose_name="Статус"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Длительность услуги"
    )

    category = models.ForeignKey(
        to = "Categories",
        on_delete=models.PROTECT,
        related_name="services",
        verbose_name="Категория"
    )

    objects = ServiceManager()

    class Meta:
        ordering = ('-created_at', )
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name
