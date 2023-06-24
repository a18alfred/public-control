from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели акаунты(юзеры), где email
    это уникальный ID/login вместо username
    """

    def create_user(self, email, password, phone_number, **extra_fields):
        """
        Создаём и созраняем акаунт с email и паролем
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        extra_fields.setdefault('is_moderator', False)
        extra_fields.setdefault('is_government', False)
        extra_fields.setdefault('is_management_company', False)
        extra_fields.setdefault('is_phone_confirmed', False)
        user.save()
        return user

    def create_superuser(self, email, password, phone_number, **extra_fields):
        """
        Создаём и сохраняем суперюзера с email и паролем
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_government', True)
        extra_fields.setdefault('is_management_company', True)
        extra_fields.setdefault('is_phone_confirmed', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser должен иметь is_superuser=True.'))
        return self.create_user(email, password, phone_number=phone_number, **extra_fields)
