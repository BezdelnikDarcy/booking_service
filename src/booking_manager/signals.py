from django.dispatch import receiver
from django.db.models.signals import post_save
from booking_manager.models import Bookings, Reviews
from .tasks import(
    send_booking_create_email_notification,
    send_review_create_email_notification
)



@receiver(post_save, sender=Bookings)
def created_booking(sender, instance, created, **kwargs):
    if created:
        send_booking_create_email_notification.delay(instance.id)



@receiver(post_save, sender=Reviews)
def created_review(sender, instance, created, **kwargs):
    if created:
        send_review_create_email_notification.delay(instance.id)
