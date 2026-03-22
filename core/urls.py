from importlib.util import find_spec

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from health_check.views import HealthCheckView
from redis.asyncio import Redis as RedisClient
from rest_framework.routers import DefaultRouter

from posts.views import PostViewSet

# Настройки роутера и дополнительных URL для документации.
router = DefaultRouter()
router.register("posts", PostViewSet, basename="posts")


urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/v1/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path(
        "api/health/",
        HealthCheckView.as_view(
            checks=[
                "health_check.Cache",
                (
                    "health_check.contrib.redis.Redis",
                    {"client_factory": lambda: RedisClient.from_url(settings.REDIS_URL)},
                ),
                "health_check.Database",
                "health_check.Storage",
            ],
        ),
        name="health-check",
    ),
]

if settings.DEBUG and find_spec("debug_toolbar") is not None:
    import debug_toolbar

    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
