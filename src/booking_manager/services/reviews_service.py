from django.core.exceptions import ValidationError
from booking_manager.models.reviews import Reviews
from booking_manager.constants import BookingStatus
from django.utils import timezone

class ReviewsService:

    @staticmethod
    def _validate_client_get_service(booking, client):
        if booking.client != client:
            raise ValidationError(
                "Отзыв может оставить только клиент из записи"
            )

    @staticmethod
    def _validate_review_on_employee_service(booking, employee):
        if booking.employee != employee:
            raise ValidationError(
                "Отзыв должен быть на мастера из записи"
            )


    @staticmethod
    def _validate_can_add_reviews_completed_booking(booking):
        if booking.status != BookingStatus.COMPLETED:
            raise ValidationError(
                "Можно оставить отзыв только после завершения записи"
            )



    @staticmethod
    def create_reviews(client, employee, service, booking, rating, **kwargs):
        #Проверка отзыва клиента на свою запись
        ReviewsService._validate_client_get_service(booking, client)
        #Проверка отзыва клиента на мастера выполнявшего запись
        ReviewsService._validate_review_on_employee_service(booking, employee)
        #Проверка отзыва, что услуга завершена
        ReviewsService._validate_can_add_reviews_completed_booking(booking)

        review = Reviews.objects.create(
            client=client,
            employee=employee,
            service=service,
            booking=booking,
            rating=rating,
            **kwargs
        )
        review.save()
        return review


    @staticmethod
    def moderate(review, is_approved=True, comment=None):
        review.is_moderated = True
        review.moderated_at = timezone.now()

        if comment:
            review.moderation_comment = comment

        if not is_approved:
            review.is_deleted = True

        review.save()

        if is_approved:
            review.employee.update_rating()
            review.employee.update_reviews_count()


    @staticmethod
    def hide(review, comment=None):
        review.is_deleted = True
        review.moderated_at = timezone.now()
        if comment:
            review.moderation_comment = comment
        review.save()

        review.employee.update_rating()
        review.employee.update_reviews_count()