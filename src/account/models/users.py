from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from account.managers import UserManager
from config.models import BaseModel


class UserType(models.TextChoices):
    CLIENT = 'client', 'Клиент'
    EMPLOYEE = 'employee', 'Мастер'
    ADMIN = 'admin', 'Администратор'


class BaseUsers(AbstractUser, PermissionsMixin, BaseModel):
    username = None
    user_type = models.CharField(
        choices=UserType,
        default=UserType.CLIENT,
        verbose_name="Тип пользователя"
    )
    phone = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Телефон"
    )

    email = models.EmailField(
        max_length=64,
        unique=True,
        verbose_name="Email"
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Заблокирован",
        help_text="Заблокированый пользователь не может создавать запиcи"
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.email}"

    class Meta:
        # verbose_name = "base_user"
        # verbose_name_plural = "base_users"
        abstract = True

class Clients(BaseUsers):
    first_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="Фамилия"
    )
    groups = models.ManyToManyField(
        to ='auth.Group',
        related_name='clients_users',
        blank=True,
        verbose_name='Группы',
    )
    user_permissions = models.ManyToManyField(
        to ='auth.Permission',
        related_name='clients_permissions',
        blank=True,
        verbose_name='Права доступа клиента',
    )

    def __str__(self):
        return f"Клиент: {self.full_name}"

    class Meta:
        ordering = ('id', "-created_at")
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class UsersAdmin(BaseUsers):
    first_name = models.CharField(
        max_length=64,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=64,
        verbose_name="Фамилия"
    )

    groups = models.ManyToManyField(
        to ='auth.Group',
        related_name='admins_users',
        blank=True,
        verbose_name='Группы',
    )
    user_permissions = models.ManyToManyField(
        to ='auth.Permission',
        related_name='admins_permissions',
        blank=True,
        verbose_name='Права доступа админа',
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type = UserType.ADMIN
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Администратор: {self.full_name}"

    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Администратор'
        verbose_name_plural = 'Админитраторы'

class Employees(BaseUsers):
    first_name = models.CharField(
        max_length=64,
        verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=64,
        verbose_name="Фамилия"
    )
    work_time_hours = models.PositiveSmallIntegerField(
        verbose_name="Часы работы в день",
        default=8,
    )
    worktime_timezone = models.SmallIntegerField(
        verbose_name="Часовой пояс",
        default=0,
    )
    rating = models.DecimalField(
        verbose_name="Рейтинг мастера",
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        max_digits=3,
        decimal_places=2,
        default=0,
    )
    specialization = models.CharField(
        verbose_name="Специализация",
        max_length=255,
        null=True,
        blank=True,
    )
    experience_years = models.PositiveSmallIntegerField(
        verbose_name="Опыт работы",
        default=0,
    )
    photo = models.ImageField(
        verbose_name="Фото мастера",
        upload_to="masters/photos/",
        null=True,
        blank=True,
    )
    is_available = models.BooleanField(
        verbose_name="Доступен для записи",
        default=False,
        help_text="Может ли мастер принимать записи"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Подтвержден",
        help_text="Подтвержден ли мастер администратором"
    )
    reviews_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество отзывов'
    )

    groups = models.ManyToManyField(
        to ='auth.Group',
        related_name='employees_users',
        blank=True,
        verbose_name='Группы',
    )
    user_permissions = models.ManyToManyField(
        to ='auth.Permission',
        related_name='employees_permissions',
        blank=True,
        verbose_name='Права доступа мастера',
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.user_type=UserType.EMPLOYEE
            self.is_verified = False
            self.is_staff = False
        super().save(*args, **kwargs)

    def update_rating(self):
        from django.db.models import Avg

        avg_rating = self.reviews.filter(
            is_moderated=True,
            is_deleted=False
        ).aggregate(Avg('rating'))['rating__avg']

        self.rating = round(avg_rating, 2) if avg_rating else 0
        self.save(update_fields=['rating'])

    def update_reviews_count(self):
        self.reviews_count = self.reviews.filter(
            is_moderated=True,
            is_deleted=False
        ).count()
        self.save(update_fields=['reviews_count'])


    def __str__(self):
        return f"Мастер: {self.full_name}"

    class Meta:
        db_table = 'employees'
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'