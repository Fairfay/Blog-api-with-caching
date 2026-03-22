from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""

    patronymic = models.CharField(
        blank=True, max_length=150,
        verbose_name="Отчество",
    )

    class Meta:
        """Мета-настройки отображения модели пользователя."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
