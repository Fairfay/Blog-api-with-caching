from typing import Any

from django.db import transaction
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiRequest,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from posts.cached import (
    get_cached_post,
    invalidate_post_cache,
    set_cached_post,
)
from posts.models import Post
from posts.serializers import PostSerializer

POST_REQUEST = {
    "application/json": PostSerializer,
    "multipart/form-data": OpenApiRequest(
        request=PostSerializer,
        encoding={
            "image": {"contentType": "image/*"},
        },
    ),
}


@extend_schema_view(
    list=extend_schema(
        tags=["Посты"],
        summary="Получить список постов",
        description="Возвращает список всех постов блога в порядке от новых к старым.",
        responses={200: PostSerializer(many=True)},
    ),
    retrieve=extend_schema(
        tags=["Посты"],
        summary="Получить пост по ID",
        description=(
            "Сначала ищет пост в Redis-кеше. Если записи нет, получает пост из "
            "PostgreSQL, сериализует его и сохраняет в кеш."
        ),
        responses={
            200: PostSerializer,
            404: OpenApiResponse(description="Пост с таким ID не найден."),
        },
    ),
    create=extend_schema(
        tags=["Посты"],
        summary="Создать пост",
        description=(
            "Создаёт новый пост. Если нужно прикрепить изображение, выберите в "
            "Swagger UI тип тела запроса `multipart/form-data` и передайте файл "
            "в поле `image`."
        ),
        request=POST_REQUEST,
        responses={
            201: PostSerializer,
            400: OpenApiResponse(description="Ошибка валидации входных данных."),
        },
        examples=[
            OpenApiExample(
                "Пример создания поста",
                description=(
                    "Пример полей для создания поста. Файл изображения "
                    "прикладывается отдельно в поле `image`."
                ),
                value={
                    "title": "Первый пост",
                    "text": "Короткий текст публикации для блога.",
                    "author": 1,
                },
                request_only=True,
            ),
        ],
    ),
    update=extend_schema(
        tags=["Посты"],
        summary="Полностью обновить пост",
        description=(
            "Полностью обновляет пост по ID и инвалидирует его кеш в Redis. "
            "Для обновления изображения используйте `multipart/form-data`."
        ),
        request=POST_REQUEST,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Ошибка валидации входных данных."),
            404: OpenApiResponse(description="Пост с таким ID не найден."),
        },
    ),
    partial_update=extend_schema(
        tags=["Посты"],
        summary="Частично обновить пост",
        description="Частично обновляет поля поста и сбрасывает кеш этой записи в Redis.",
        request=POST_REQUEST,
        responses={
            200: PostSerializer,
            400: OpenApiResponse(description="Ошибка валидации входных данных."),
            404: OpenApiResponse(description="Пост с таким ID не найден."),
        },
    ),
    destroy=extend_schema(
        tags=["Посты"],
        summary="Удалить пост",
        description="Удаляет пост по ID и инвалидирует его кеш в Redis.",
        responses={
            204: OpenApiResponse(description="Пост успешно удалён."),
            404: OpenApiResponse(description="Пост с таким ID не найден."),
        },
    ),
)
class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD-операций над постами и работы с кешем."""

    queryset = Post.objects.select_related("author")
    serializer_class = PostSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Возвращает пост из кеша или прогревает кеш при его отсутствии."""
        post_id = self.kwargs["pk"]
        cached_post = get_cached_post(post_id)

        if cached_post is not None:
            return Response(cached_post)

        response = super().retrieve(request, *args, **kwargs)
        set_cached_post(post_id, response.data)
        return response

    def perform_update(self, serializer: Any) -> None:
        """Обновляет пост и сбрасывает его кеш."""
        with transaction.atomic():
            post = serializer.save()
            transaction.on_commit(lambda post_id=post.pk: invalidate_post_cache(post_id))

    def perform_destroy(self, instance: Post) -> None:
        """Удаляет пост и инвалидирует связанный ключ в кеше."""
        post_id = instance.pk

        with transaction.atomic():
            instance.delete()
            transaction.on_commit(lambda post_id=post_id: invalidate_post_cache(post_id))
