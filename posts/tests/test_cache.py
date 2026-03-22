import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from posts.cached import get_post_cache_key
from posts.models import Post

pytestmark = pytest.mark.django_db


def test_retrieve_populates_cache_and_reuses_cached_payload(
    api_client: APIClient,
    post: Post,
    detail_url: str,
) -> None:
    """Прогревает кеш при первом чтении и повторно использует закешированные данные."""
    first_response = api_client.get(detail_url)

    assert first_response.status_code == status.HTTP_200_OK
    assert first_response.json()["text"] == post.text

    cache_key = get_post_cache_key(post.pk)
    cached_payload = cache.get(cache_key)

    assert cached_payload is not None
    assert cached_payload["title"] == post.title

    Post.objects.filter(pk=post.pk).update(
        text="Текст в базе изменён после прогрева кеша.",
    )

    second_response = api_client.get(detail_url)

    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.json()["text"] == "Исходный текст из базы данных."


def test_update_and_delete_invalidate_post_cache(
    api_client: APIClient,
    detail_url: str,
    post: Post,
) -> None:
    """Инвалидирует кеш поста после обновления и удаления."""
    api_client.get(detail_url)

    cache_key = get_post_cache_key(post.pk)
    assert cache.get(cache_key) is not None

    update_response = api_client.patch(
        detail_url,
        {"title": "Обновлённый заголовок", "text": "Обновлённый текст"},
        format="json",
    )

    assert update_response.status_code == status.HTTP_200_OK
    assert cache.get(cache_key) is None

    api_client.get(detail_url)
    assert cache.get(cache_key) is not None

    delete_response = api_client.delete(detail_url)

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert cache.get(cache_key) is None
