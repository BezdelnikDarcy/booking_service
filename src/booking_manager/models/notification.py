from django.db import models

from config.models import BaseModel
from booking_manager.constants import NotificationType, NotificationChannel, NotificationStatus



class Notification(BaseModel):
    booking = models.ForeignKey(
        to="Bookings",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )

    recipient = models.ForeignKey(
        to="account.Users",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Получатель"
    )

    notification_type = models.CharField(
        choices=NotificationType,
        verbose_name="Тип уведомления"
    )

    channel = models.CharField(
        choices=NotificationChannel,
        default=NotificationChannel.SMS,
        verbose_name="Канал отправки"
    )

    status = models.CharField(
        choices=NotificationStatus,
        default=NotificationStatus.CREATED,
        verbose_name="Статус"
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Заголовок"
    )

    message = models.TextField(
        verbose_name="Текст"
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата отправки"
    )

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"