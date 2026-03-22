from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Post(models.Model):
    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок"
    )
    text = models.TextField(
        verbose_name="Содержание"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата и время обновления"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    image = models.ImageField(
        blank=True,
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_at"], name="post_created_at_idx"),
        ]

    def __str__(self):
        return f"Пост {self.title[:20]} от автора {self.author.username}"
