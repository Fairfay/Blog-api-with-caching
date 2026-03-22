import pytest
from django.core.cache import cache
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from identity.models import User
from posts.models import Post


@pytest.fixture(autouse=True)
def clear_post_cache() -> None:
    """Очищает кеш до и после каждого теста."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client() -> APIClient:
    """Возвращает DRF-клиент для интеграционных тестов."""
    return APIClient()


@pytest.fixture
def author(db: None) -> User:
    """Создаёт тестового автора в тестовой базе данных."""
    return baker.make(User, username="автор-кеша")


@pytest.fixture
def post(db: None, author: User) -> Post:
    """Создаёт пост, связанный с тестовым автором."""
    return baker.make(
        Post,
        author=author,
        title="Закешированный пост",
        text="Исходный текст из базы данных.",
    )


@pytest.fixture
def detail_url(post: Post) -> str:
    """Собирает URL детального эндпоинта для поста."""
    return reverse("posts-detail", args=[post.pk])
