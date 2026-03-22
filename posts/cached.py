import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)


def get_post_cache_key(post_id: int | str) -> str:
    return f"post:{post_id}"


def _log_redis_unavailable(action: str, post_id: int | str) -> None:
    logger.warning(
        "Redis is unavailable while %s cache for post %s.",
        action,
        post_id,
        exc_info=True,
    )


def get_cached_post(post_id: int | str) -> dict[str, Any] | None:
    try:
        return cache.get(get_post_cache_key(post_id))
    except RedisError:
        _log_redis_unavailable("reading", post_id)
        return None


def set_cached_post(post_id: int | str, payload: dict[str, Any]) -> None:
    try:
        cache.set(
            get_post_cache_key(post_id),
            payload,
            timeout=settings.POST_CACHE_TIMEOUT,
        )
    except RedisError:
        _log_redis_unavailable("writing", post_id)


def invalidate_post_cache(post_id: int | str) -> None:
    try:
        cache.delete(get_post_cache_key(post_id))
    except RedisError:
        _log_redis_unavailable("invalidating", post_id)
