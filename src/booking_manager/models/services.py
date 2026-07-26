from django.db import models

from config.models import BaseModel
from booking_manager.constants import ServiceStatus
from booking_manager.managers import ServiceManager


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

    status = models.CharField(
        choices=ServiceStatus,
        default=ServiceStatus.INACTIVE,
        verbose_name="Статус"
    )


    category = models.ForeignKey(
        to = "Categories",
        on_delete=models.PROTECT,
        related_name="services",
        verbose_name="Категория"
    )
    image = models.ImageField(
        upload_to="services/",
        blank=True,
        null=True,
        verbose_name="Изображение услуги"
    )
    objects = ServiceManager()

    class Meta:
        ordering = ['category', 'name',]
        db_table = 'services'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.name
