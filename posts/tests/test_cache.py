from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from posts.models import Post
from posts.services import get_post_cache_key


User = get_user_model()


class PostCacheIntegrationTests(APITestCase):
    def setUp(self):
        super().setUp()
        cache.clear()
        self.author = User.objects.create_user(
            username="cache-author",
            password="strong-test-password",
        )
        self.post = Post.objects.create(
            title="Cached post",
            text="Initial text from the database.",
            author=self.author,
        )
        self.detail_url = reverse("posts-detail", args=[self.post.pk])

    def tearDown(self):
        cache.clear()
        super().tearDown()

    def test_retrieve_populates_cache_and_reuses_cached_payload(self):
        first_response = self.client.get(self.detail_url)

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(first_response.json()["text"], self.post.text)

        cache_key = get_post_cache_key(self.post.pk)
        cached_payload = cache.get(cache_key)

        self.assertIsNotNone(cached_payload)
        self.assertEqual(cached_payload["title"], self.post.title)

        Post.objects.filter(pk=self.post.pk).update(
            text="Database text changed after cache warmup.",
        )

        second_response = self.client.get(self.detail_url)

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            second_response.json()["text"],
            "Initial text from the database.",
        )

    def test_update_and_delete_invalidate_post_cache(self):
        self.client.get(self.detail_url)

        cache_key = get_post_cache_key(self.post.pk)
        self.assertIsNotNone(cache.get(cache_key))

        update_response = self.client.patch(
            self.detail_url,
            {"title": "Updated title", "text": "Updated text"},
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(cache.get(cache_key))

        self.client.get(self.detail_url)
        self.assertIsNotNone(cache.get(cache_key))

        delete_response = self.client.delete(self.detail_url)

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(cache.get(cache_key))
