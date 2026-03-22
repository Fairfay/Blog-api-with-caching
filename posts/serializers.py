from django.contrib.auth import get_user_model
from rest_framework import serializers

from posts.models import Post

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания, обновления и чтения постов."""

    id = serializers.IntegerField(
        read_only=True,
        help_text="Уникальный идентификатор поста.",
    )
    title = serializers.CharField(
        max_length=256,
        help_text="Заголовок поста.",
    )
    text = serializers.CharField(
        help_text="Основное содержимое поста.",
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        help_text="Идентификатор автора поста.",
    )
    image = serializers.ImageField(
        required=False,
        allow_null=True,
        help_text=(
            "Изображение поста. Для загрузки через Swagger UI выберите " "`multipart/form-data`."
        ),
    )
    created_at = serializers.DateTimeField(
        read_only=True,
        help_text="Дата и время создания поста.",
    )
    updated_at = serializers.DateTimeField(
        read_only=True,
        help_text="Дата и время последнего обновления поста.",
    )

    class Meta:
        """Настройки сериализатора поста."""

        model = Post
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
