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


def send_notification(
        booking,
        recipient,
        title,
        message,
        notification_type,
):
    now = timezone.now()
    try:
        result = send_mail(
            subject=title,
            message=message,
            recipient_list=[recipient.email],
            from_email=settings.DEFAULT_FROM_EMAIL, )
        if not result:
            raise RuntimeError("Письмо не отправлено")
        status = NotificationStatus.SENT
    except Exception as e:
        logger.exception(
            f"Ошибка отправки уведомления для записи {booking.id}: {e}"
        )
        status = NotificationStatus.FAILED


    Notification.objects.create(
        booking=booking,
        recipient=recipient,
        notification_type=notification_type,
        channel=NotificationChannel.EMAIL,
        status=status,
        title=title,
        message=message,
        sent_at=now,
    )

    #Возвращаем True при успешной отправки сообщения(необходимо для некоторых функций)
    return status == NotificationStatus.SENT

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
            f"{booking.service.name}.\n\n"
            f"Ждём вас!"
        )
        sent = send_notification(
            booking=booking,
            recipient=booking.client.user,
            title=title,
            message=message,
            notification_type=NotificationType.BOOKING_REMINDER,
        )
        if sent:
            booking.reminder_sent = True
            booking.save(update_fields=['reminder_sent'])




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

@shared_task
def send_booking_create_email_notification(booking_id):
    booking = Bookings.objects.select_related(
        "client__user",
        "employee_service__employee__user",
        "employee_service__service",
    ).get(id=booking_id)
    client_title = "Подтверждение записи"
    master_title = "Новая запись"
    message_to_client = (
        f"Здравствуйте, {booking.client.user.full_name}!\n\n"
        f"Ваша запись на услугу {booking.service.name} успешно подтверждена на {booking.start_at:%d.%m.%Y %H:%M} "
        f"Ждём вас!"
    )
    message_to_master = (
        f"Здравствуйте, {booking.employee.user.full_name}!\n\n"
        f"Клиент {booking.client.user.full_name} создал запись услуги {booking.service.name} на {booking.start_at:%d.%m.%Y %H:%M}"
    )
    notification_type = NotificationType.BOOKING_CREATED
    #отправка сообщения на почту клиенту
    send_notification(
        booking=booking,
        recipient=booking.client.user,
        title=client_title,
        notification_type=notification_type,
        message=message_to_client,
    )
    #Отправка сообщения о создании записи мастеру
    send_notification(
        booking=booking,
        recipient=booking.employee.user,
        title=master_title,
        notification_type=notification_type,
        message=message_to_master,
    )


@shared_task
def send_booking_canceled_email_notification(booking_id):
    booking = Bookings.objects.select_related(
        "client__user",
        "employee_service__employee__user",
        "employee_service__service",
    ).get(id=booking_id)
    title = "Отмена записи"
    message_to_client = (
        f"Здравствуйте, {booking.client.user.full_name}!\n\n"
        f"Ваша запись {booking.start_at:%d.%m.%Y %H:%M} на услугу {booking.service.name} отменена "
    )
    message_to_master = (
        f"Здравствуйте, {booking.employee.user.full_name}!\n\n"
        f"Запись клиент {booking.client.user.full_name} на {booking.start_at:%d.%m.%Y %H:%M} отменена"
    )
    notification_type = NotificationType.BOOKING_CANCELLED
    #Отправка сообщения об отмене на почту клиенту
    send_notification(
        booking=booking,
        recipient=booking.client.user,
        title=title,
        notification_type=notification_type,
        message=message_to_client,
    )
    #Отправка сообщения об отмене записи мастеру
    send_notification(
        booking=booking,
        recipient=booking.employee.user,
        title=title,
        notification_type=notification_type,
        message=message_to_master,
    )

@shared_task
def send_booking_rescheduled_email_notification(new_booking_id):
    new_booking = (Bookings.objects.select_related(
        "client__user",
        "employee_service__employee__user",
        "employee_service__service",
        "rescheduled_from__employee_service__service",
        "rescheduled_from__client__user",
    ).get(id=new_booking_id))
    old_booking = new_booking.rescheduled_from
    title = "Перенос записи"
    message_to_client = (
        f"Здравствуйте, {new_booking.client.user.full_name}!\n\n"
        f"Ваша запись {old_booking.start_at:%d.%m.%Y %H:%M} на услугу {old_booking.service.name} перенесена"
        f" на {new_booking.start_at:%d.%m.%Y %H:%M}, Если вы не запрашивали перенос записи, пожалуйста, свяжитесь с администрацией салона."
    )
    message_to_master = (
        f"Здравствуйте, {new_booking.employee.user.full_name}!\n\n"
        f"Запись клиента {old_booking.client.user.full_name} на {old_booking.start_at:%d.%m.%Y %H:%M} перенесена"
        f" на {new_booking.start_at:%d.%m.%Y %H:%M}"
    )
    notification_type = NotificationType.BOOKING_RESCHEDULED
    # Отправка сообщения о переносе на почту клиенту
    send_notification(
        booking=new_booking,
        recipient=new_booking.client.user,
        title=title,
        notification_type=notification_type,
        message=message_to_client,
    )
    # Отправка сообщения о переносе записи мастеру
    send_notification(
        booking=new_booking,
        recipient=new_booking.employee.user,
        title=title,
        notification_type=notification_type,
        message=message_to_master,
    )

