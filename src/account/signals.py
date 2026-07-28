from django.core.mail import send_mail
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

@receiver(reset_password_token_created)
def send_password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Отправляет письмо со ссылкой для сброса пароля.
    """
    # 1. Формируем ссылку для сброса пароля
    reset_url = instance.request.build_absolute_uri(
        reverse('password_reset:reset-password-confirm')
    ) + f"?token={reset_password_token.key}"

    # 2. Текст письма (простой, без HTML)
    message = f"""
Здравствуйте!
Вы запросили восстановление пароля на сайте ....
Для установки нового пароля перейдите по ссылке:
{reset_url}
Если вы не запрашивали восстановление пароля — проигнорируйте это письмо.
"""
    # 3. Отправляем письмо
    send_mail(
        subject="Восстановление пароля салона красоты",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reset_password_token.user.email],
        fail_silently=False,
    )