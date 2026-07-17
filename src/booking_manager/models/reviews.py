from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from config.models import BaseModel


class Reviews(BaseModel):
    client = models.ForeignKey(
        to='account.Clients',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Клиент'
    )
    employee = models.ForeignKey(
        to='account.Employees',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Мастер'
    )
    service = models.ForeignKey(
        to='Services',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Услуга'
    )
    booking = models.ForeignKey(
        to='Bookings',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Запись'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Оценка должна быть не менее 1'),
            MaxValueValidator(5, message='Оценка должна быть не более 5')
        ],
        verbose_name='Оценка (1-5)'
    )
    text = models.TextField(
        verbose_name='Текст отзыва',
        blank=True,
        null=True
    )

    is_moderated = models.BooleanField(
        default=False,
        verbose_name='Отзыв прошел модерацию'
    )
    moderated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата модерации'
    )
    moderation_comment = models.TextField(
        blank=True,
        verbose_name='Комментарий модератора'
    )

    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удален (для скрытия без удаления из БД)'
    )

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-created_at',)
        unique_together = ['client', 'booking']

    def __str__(self):
        return f"Отзыв {self.client.full_name} на {self.employee.full_name} - {self.rating}★"

    @property
    def is_positive(self):
        return self.rating >= 4

    @property
    def is_negative(self):
        return self.rating <= 2

    def moderate(self, is_approved=True, comment=None):
        self.is_moderated = True
        self.moderated_at = timezone.now()

        if comment:
            self.moderation_comment = comment

        if not is_approved:
            self.is_deleted = True

        self.save()

        if is_approved:
            self.employee.update_rating()
            self.employee.update_reviews_count()

    def hide(self, comment=None):
        self.is_deleted = True
        self.moderated_at = timezone.now()
        if comment:
            self.moderation_comment = comment
        self.save()

        self.employee.update_rating()
        self.employee.update_reviews_count()