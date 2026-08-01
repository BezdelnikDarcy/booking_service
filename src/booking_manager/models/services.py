from django.db import models
from django.core.exceptions import ValidationError
from config.models import BaseModel
from booking_manager.constants import ServiceStatus, BookingStatus
from booking_manager.managers import ServiceManager
from booking_manager.models.bookings import Bookings


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
        upload_to="services/images",
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


    def clean(self):
        if self.pk:
            old_status = Services.objects.get(pk=self.pk).status
            if old_status == ServiceStatus.ACTIVE and self.status != ServiceStatus.INACTIVE:
                has_activ_booking = Bookings.objects.filter(
                    employee_service__service=self,
                    status=BookingStatus.CONFIRMED,
                ).exists()
                if has_activ_booking:
                    raise ValidationError(
                        "Отмените активные записи, после чего можно будет совершить деактивацию или архивирование услуги"
                    )

    def save(self, *args, **kwargs):
        status_changed = False

        if self.pk:
            old_status = Services.objects.get(pk=self.pk).status
            status_changed = old_status != self.status

        self.full_clean()
        super().save(*args, **kwargs)

        if status_changed and self.status != ServiceStatus.ACTIVE:
            self.employee_services.update(is_active=False)