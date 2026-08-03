import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # Напоминание о бронировании
    'booking-reminders': {
        'task': 'booking_manager.tasks.send_booking_reminder_notifications',
        'schedule': crontab(minute="*/15"),
    },
    # Завершение услуг
    'completed-booking': {
        'task': 'booking_manager.tasks.completed_booking',
        'schedule': crontab(minute="*/5"),
    },
    # Обновление рейтинга
    'update-ratings': {
        'task': 'booking_manager.tasks.update_rating_masters',
        'schedule': crontab(hour=1, minute=0),
    },
    # Удаление старых уведомлений
    'delete-old-notifications': {
        'task': 'booking_manager.tasks.delete_old_notifications',
        'schedule': crontab(day_of_week=1, hour=6, minute=0),
    },
    # Деактивация промо-кодов
    'deactivate-promo-codes': {
        'task': 'booking_manager.tasks.deactivate_promo_codes',
        'schedule': crontab(hour=0, minute=0),
    },
}