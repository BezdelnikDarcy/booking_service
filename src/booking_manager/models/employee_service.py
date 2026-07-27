from decimal import Decimal
from datetime import timedelta
from django.db import models
from config.models import BaseModel
from django.core.validators import MinValueValidator
from booking_manager.constants import ServiceStatus
from booking_manager.models.services import Services
from django.core.exceptions import ValidationError


class EmployeeService(BaseModel):
    employee = models.ForeignKey(
        to = "account.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="employee_services",
        verbose_name="Мастер"
    )

    service = models.ForeignKey(
        to = "Services",
        on_delete=models.PROTECT,
        related_name="employee_services",
        verbose_name="Услуга"
    )

    price = models.DecimalField(
        validators = [MinValueValidator(Decimal("0.01"))],
        max_digits=10,
        decimal_places=2,
        verbose_name="Стоимость"
    )

    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(10)],
        verbose_name="Длительность услуги в минутах"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Доступна"
    )

    class Meta:
        ordering = ["service", "employee"]
        db_table = "employee_services"
        verbose_name = "Услуга мастера"
        verbose_name_plural = "Услуги мастеров"
        indexes = [
            models.Index(fields=["employee"]),
            models.Index(fields=["service"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee", "service"],
                name="unique_employee_service"
            )
        ]

    def __str__(self):
        return f"{self.employee.user.full_name} - {self.service.name}"

    def calculate_end_time(self, start_at):
        return start_at + timedelta(minutes=self.duration)

    def clean(self):
        if not self.is_available_service():
            raise ValidationError({
                'service': 'Услуга недоступна',
            })

    def is_available_service(self):
        return self.service.status == ServiceStatus.ACTIVE