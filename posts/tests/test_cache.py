import pytest
from django.core.cache import cache
from rest_framework import status

from posts.models import Post
from posts.cached import get_post_cache_key


pytestmark = pytest.mark.django_db


def test_retrieve_populates_cache_and_reuses_cached_payload(api_client, post, detail_url) -> None:
    first_response = api_client.get(detail_url)

    assert first_response.status_code == status.HTTP_200_OK
    assert first_response.json()['text'] == post.text

    cache_key = get_post_cache_key(post.pk)
    cached_payload = cache.get(cache_key)

    assert cached_payload is not None
    assert cached_payload['title'] == post.title

    Post.objects.filter(pk=post.pk).update(
        text='Database text changed after cache warmup.',
    )

    second_response = api_client.get(detail_url)

    assert second_response.status_code == status.HTTP_200_OK
    assert second_response.json()['text'] == 'Initial text from the database.'


def test_update_and_delete_invalidate_post_cache(api_client, detail_url, post) -> None:
    api_client.get(detail_url)

    cache_key = get_post_cache_key(post.pk)
    assert cache.get(cache_key) is not None

    update_response = api_client.patch(
        detail_url,
        {'title': 'Updated title', 'text': 'Updated text'},
        format='json',
    )

    assert update_response.status_code == status.HTTP_200_OK
    assert cache.get(cache_key) is None

    api_client.get(detail_url)
    assert cache.get(cache_key) is not None

    delete_response = api_client.delete(detail_url)

    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert cache.get(cache_key) is None
