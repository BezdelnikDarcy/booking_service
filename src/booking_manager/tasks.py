from celery import shared_task
from django.core.mail import send_mail
from datetime import timedelta
from booking_manager.models import Bookings, Notification, PromoCodes
from django.utils import timezone
from booking_manager.constants import BookingStatus, NotificationType, NotificationChannel, NotificationStatus
from django.conf import settings
from account.models.users import EmployeeProfile
import logging


logger = logging.getLogger(__name__)




@shared_task
def send_booking_reminder_notifications():
    #Отправка уведомлений за 24 часа до записи
    now = timezone.now()
    bookings = Bookings.objects.filter(
        status=BookingStatus.CONFIRMED,
        start_at__gt=now,
        start_at__lte=now+timedelta(hours=24),
        reminder_sent=False,
    )
    for booking in bookings:
        title = f"Напоминание о записи {booking.start_at:%d.%m.%Y %H:%M}"
        message=(
            f"Здравствуйте, {booking.client.user.full_name}!\n\n"
            f"Напоминаем, что завтра у вас запись в {booking.start_at:%H:%M} на услугу "
            f"{booking.employee_service.service.name}.\n\n"
            f"Ждём вас!"
        )
        try:
            result = send_mail(
                subject=title,
                message=message,
                recipient_list=[booking.client.user.email],
                from_email=settings.DEFAULT_FROM_EMAIL,)
            if not result:
                raise RuntimeError("Письмо не отправлено")
            booking.reminder_sent = True
            booking.save(update_fields=['reminder_sent'])
            Notification.objects.create(
                booking=booking,
                recipient=booking.client.user,
                notification_type=NotificationType.BOOKING_REMINDER,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.SENT,
                title=title,
                message=message,
                sent_at=now,
            )
        except Exception as e:
            Notification.objects.create(
                booking=booking,
                recipient=booking.client.user,
                notification_type=NotificationType.BOOKING_REMINDER,
                channel=NotificationChannel.EMAIL,
                status=NotificationStatus.FAILED,
                title=title,
                message=message,
                sent_at=now,
            )
            logger.exception(
                f"Ошибка отправки напоминания для {booking.id}: {e}"
            )
            raise



@shared_task
def completed_booking():
    #Авто-выполнение услуг
    now = timezone.now()
    Bookings.objects.filter(
        end_at__lte=now,
        status=BookingStatus.CONFIRMED,
    ).update(status=BookingStatus.COMPLETED)


@shared_task
def update_rating_masters():
    employees = EmployeeProfile.objects.filter(is_verified=True)
    for employee in employees:
        employee.update_rating()


@shared_task
def delete_old_notifications():
    now = timezone.now()
    Notification.objects.filter(
        created_at__lte=now-timedelta(days=31),
    ).delete()


@shared_task
def deactivate_promo_codes():
    now = timezone.now()
    PromoCodes.objects.filter(
        valid_until__lte=now,
        is_active=True,
    ).update(
        is_active=False,
    )


# @shared_task
# def scheduled_task_every_3_min_40_sec():
#     #Выполняется каждые 3 минуты 40 секунд
#     print(f"Task executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
#     return f"Scheduled task completed at {time.strftime('%H:%M:%S')}"
#
#
# @shared_task
# def scheduled_task_limited_times():
#     #Выполняется 3 раза с 19 по 21 число каждый час
#     print(f"Limited task executed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
#     return f"Limited task completed"
#
# @shared_task
# def solar_sunrise_greeting():
#     #Отправляет приветствие на восходе солнца
#     admins = User.objects.filter(is_superuser=True)
#     for admin in admins:
#         print(f"🌅 Good morning {admin.username}! The sun has risen!")
#         # Здесь реальная отправка email
#     return "Sunrise greetings sent"
#
# @shared_task
# def weekly_email_newsletter():
#     #Еженедельная рассылка email
#     users = User.objects.filter(is_active=True)
#     for user in users:
#         print(f"📧 Weekly newsletter sent to {user.email}")
#         # Здесь реальная отправка email
#     return f"Weekly newsletter sent to {users.count()} users"