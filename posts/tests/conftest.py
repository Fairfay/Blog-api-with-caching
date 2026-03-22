import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from posts.models import Post


User = get_user_model()

@pytest.fixture(autouse=True)
def clear_post_cache() -> None:
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def author(db):
    return baker.make(User, username='cache-author')


@pytest.fixture
def post(db, author):
    return baker.make(
        Post,
        author=author,
        title='Cached post',
        text='Initial text from the database.',
    )


@pytest.fixture
def detail_url(post) -> str:
    return reverse('posts-detail', args=[post.pk])
