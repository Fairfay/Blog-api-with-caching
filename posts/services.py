import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)


def get_post_cache_key(post_id: int | str) -> str:
    return f"post:{post_id}"


def get_cached_post(post_id: int | str) -> dict[str, Any] | None:
    try:
        return cache.get(get_post_cache_key(post_id))
    except RedisError:
        logger.warning(
            "Redis is unavailable while reading post %s from cache.",
            post_id,
            exc_info=True,
        )
        return None


def set_cached_post(post_id: int | str, payload: dict[str, Any]) -> None:
    try:
        cache.set(
            get_post_cache_key(post_id),
            payload,
            timeout=settings.POST_CACHE_TIMEOUT,
        )
    except RedisError:
        logger.warning(
            "Redis is unavailable while writing post %s to cache.",
            post_id,
            exc_info=True,
        )


def invalidate_post_cache(post_id: int | str) -> None:
    try:
        cache.delete(get_post_cache_key(post_id))
    except RedisError:
        logger.warning(
            "Redis is unavailable while invalidating post %s cache.",
            post_id,
            exc_info=True,
        )
