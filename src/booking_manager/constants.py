from django.db import models



class ServiceStatus(models.TextChoices):
    ACTIVE = 'active', 'Активна'
    INACTIVE = 'inactive', 'Неактивна'
    ARCHIVED = 'archived', 'Архивирована'


class DiscountType(models.TextChoices):
    PERCENT = "percent", "Процент"
    FIXED = "fixed", "Фиксированная сумма"

class NotificationType(models.TextChoices):
    BOOKING_CREATED = "booking_created", "Создание записи"
    BOOKING_CANCELLED = "booking_cancelled", "Запись отменена"
    BOOKING_RESCHEDULED = "booking_rescheduled", "Запись перенесена"
    BOOKING_REMINDER = "booking_reminder", "Напоминание о записи"
    REVIEW_CREATED = "review_created", "Новый отзыв"
    SYSTEM = "system", "Системное"

class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    SMS = "sms", "SMS"
    IN_APP = "in_app", "В приложении"

class NotificationStatus(models.TextChoices):
    CREATED = "created", "Создано"
    SENT = "sent", "Отправлено"
    FAILED = "failed", "Ошибка"

class BookingStatus(models.TextChoices):
    CONFIRMED = 'confirmed', 'Подтверждена'
    COMPLETED = 'completed', 'Выполнена'
    CANCELLED = 'cancelled', 'Отменена'
    NO_SHOW = 'no_show', 'Не явился'
    RESCHEDULED = 'rescheduled', 'Перенесена'

class Weekday(models.IntegerChoices):
    MONDAY = 0, "Понедельник"
    TUESDAY = 1, "Вторник"
    WEDNESDAY = 2, "Среда"
    THURSDAY = 3, "Четверг"
    FRIDAY = 4, "Пятница"
    SATURDAY = 5, "Суббота"
    SUNDAY = 6, "Воскресенье"
