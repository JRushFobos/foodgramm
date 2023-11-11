from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api.validators import validate_name, validate_username


class User(AbstractUser):
    """Модель пользователей"""

    email = models.EmailField(
        "Email",
        max_length=settings.MAX_EMAIL_LENGTH,
        unique=True,
    )

    username = models.CharField(
        "Имя пользователя",
        unique=True,
        max_length=settings.USERNAME_MAX_CHAR_LENGTH,
        validators=[validate_username, UnicodeUsernameValidator()],
    )

    first_name = models.CharField(
        "Имя",
        max_length=settings.USERNAME_MAX_CHAR_LENGTH,
        validators=[validate_name],
    )

    last_name = models.CharField(
        "Фамилия",
        max_length=settings.USERNAME_MAX_CHAR_LENGTH,
        validators=[validate_name],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписчиков."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribes",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписчики"

        constraints = (
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="no_self_subscribe",
            ),
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_subscription"
            ),
        )

    def __str__(self):
        return f"Подписка {self.user} на {self.author}"
