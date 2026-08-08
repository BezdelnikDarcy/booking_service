from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.managers import UserManager
from config.models import BaseModel


class UserType(models.TextChoices):
    CLIENT = 'client', 'Клиент'
    EMPLOYEE = 'employee', 'Мастер'
    ADMIN = 'admin', 'Администратор'


class Users(AbstractUser, PermissionsMixin, BaseModel):
    username = None
    user_type = models.CharField(
        choices=UserType,
        default=UserType.CLIENT,
        verbose_name="Тип пользователя"
    )
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

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_user_type = None

        if not is_new:
            old_user_type = Users.objects.get(pk=self.pk).user_type

        self.is_staff = self.user_type in (
            UserType.ADMIN,
            UserType.EMPLOYEE,
        )
        super().save(*args, **kwargs)

        if not is_new and old_user_type == self.user_type:
            return

        if is_new:
            self._create_profile()
        else:
            self._switch_profile(old_user_type)

    def _create_profile(self):
        profile = None
        created = False
        if self.user_type == UserType.CLIENT:
            profile, created = ClientProfile.objects.get_or_create(user=self)
        elif self.user_type == UserType.EMPLOYEE:
            profile, created = EmployeeProfile.objects.get_or_create(user=self)
        elif self.user_type == UserType.ADMIN:
            profile, created = AdminProfile.objects.get_or_create(user=self)


        if not created and not profile.is_active:
            profile.is_active = True
            profile.save()

    def _switch_profile(self, old_user_type):
        if old_user_type == UserType.CLIENT and hasattr(self, 'client_profile'):
            self.client_profile.is_active = False
            self.client_profile.save()
        elif old_user_type == UserType.EMPLOYEE and hasattr(self, 'employee_profile'):
            self.employee_profile.is_active = False
            self.employee_profile.save()
        elif old_user_type == UserType.ADMIN and hasattr(self, 'admin_profile'):
            self.admin_profile.is_active = False
            self.admin_profile.save()



        self._create_profile()


    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return f"{self.email}"

    class Meta:
        ordering = ["-created_at"]
        db_table = "users"
        verbose_name = "user"
        verbose_name_plural = "users"

class ClientProfile(BaseModel):
    user = models.OneToOneField(
        to="account.Users",
        on_delete=models.CASCADE,
        related_name="client_profile",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный профиль",
    )

    def __str__(self):
        return f"Клиент: {self.user.full_name}"

    class Meta:
        ordering = ('id', "-created_at")
        db_table = 'clients'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class AdminProfile(BaseModel):
    user = models.OneToOneField(
        to="account.Users",
        on_delete=models.CASCADE,
        related_name="admin_profile"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный профиль",
    )


    def __str__(self):
        return f"Администратор: {self.user.full_name}"

    class Meta:
        db_table = 'admin_users'
        verbose_name = 'Администратор'
        verbose_name_plural = 'Админитраторы'

class EmployeeProfile(BaseModel):
    user = models.OneToOneField(
        to="account.Users",
        on_delete=models.CASCADE,
        related_name="employee_profile"
    )
    work_time_hours = models.PositiveSmallIntegerField(
        verbose_name="Часы работы в день",
        default=8,
    )
    timezone_offset = models.SmallIntegerField(
        verbose_name="Часовой пояс",
        default=3,
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
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активный профиль",
    )


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
        return f"Мастер: {self.user.full_name}"

    class Meta:
        db_table = 'employees'
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'