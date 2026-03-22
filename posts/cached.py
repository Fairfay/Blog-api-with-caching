import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def get_post_cache_key(post_id: int | str) -> str:
    """Возвращает ключ кеша для конкретного поста."""
    return f"post:{post_id}"


def _log_redis_unavailable(action: str, post_id: int | str) -> None:
    logger.warning(
        "Redis недоступен при %s кеша поста %s.",
        action,
        post_id,
        exc_info=True,
    )


def get_cached_post(post_id: int | str) -> dict[str, Any] | None:
    """Читает сериализованный пост из кеша."""
    try:
        return cache.get(get_post_cache_key(post_id))
    except RedisError:
        _log_redis_unavailable("чтении", post_id)
        return None


def set_cached_post(post_id: int | str, payload: dict[str, Any]) -> None:
    """Сохраняет сериализованный пост в кеш."""
    try:
        cache.set(
            get_post_cache_key(post_id),
            payload,
            timeout=settings.POST_CACHE_TIMEOUT,
        )
    except RedisError:
        _log_redis_unavailable("записи", post_id)


def invalidate_post_cache(post_id: int | str) -> None:
    """Удаляет пост из кеша по его идентификатору."""
    try:
        cache.delete(get_post_cache_key(post_id))
    except RedisError:
        _log_redis_unavailable("инвалидации", post_id)
