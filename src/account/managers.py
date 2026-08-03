from django.contrib.auth.base_user import BaseUserManager

from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    def _create_user(self, email, password, phone = None, **kwargs):
        if not email:
            raise ValueError('email обяательный')
        user = self.model(email=email, phone=phone, **kwargs)
        user.password = make_password(password)
        user.save()
        return user

    def create_user(self, email, password, phone = None, **kwargs):
        if not phone:
            raise ValueError('Телефон обязатален')
        return self._create_user(email, password, phone, **kwargs)

    def create_superuser(self, email, password, phone = None):
        kwargs ={
            'is_staff': True,
            'is_superuser': True,
        }

        return self._create_user(email, password, phone, **kwargs)