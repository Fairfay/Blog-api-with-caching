import os
import sys
import tomllib
from importlib.util import find_spec
from pathlib import Path

import structlog
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent
IS_RUNNING_TESTS = "pytest" in sys.modules

SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-local-development-key",
)

DEBUG = config(
    "DJANGO_DEBUG",
    cast=bool,
    default=False,
)

ALLOWED_HOSTS = config(
    "DJANGO_ALLOWED_HOSTS",
    cast=Csv(),
    default="127.0.0.1,localhost",
)

# Настройка приложений: Django, сторонние и локальные.
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_structlog",
    "drf_standardized_errors",
    "django.contrib.postgres",
    "health_check",
    "drf_spectacular",
]

LOCAL_APPS = [
    "identity.apps.IdentityConfig",
    "posts.apps.PostsConfig",
]


def is_optional_module_available(module_name: str) -> bool:
    """Проверить доступность необязательного Python-модуля."""
    return find_spec(module_name) is not None


def extend_enabled_items(target: list[str], *items: tuple[bool, str]) -> None:
    """Добавить элементы в список настроек только для включённых условий."""
    target.extend(value for enabled, value in items if enabled)


INSTALLED_APPS = [
    *DJANGO_APPS,
    *THIRD_PARTY_APPS,
    *LOCAL_APPS,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# База данных по умолчанию.
DATABASES = {
    "default": {
        "ENGINE": config("POSTGRES_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("POSTGRES_DB", default="blog_api"),
        "USER": config("POSTGRES_USER", default="blog_user"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="blog_password"),
        "HOST": config("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": config("POSTGRES_PORT", default="5432"),
    },
}


# Валидация паролей по умолчанию.
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Настройки языка, времени и даты.
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

USE_I18N = True

USE_TZ = True


# Статика и медиа.
STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "identity.User"

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Дополнительные настройки в режиме DEBUG.
if DEBUG:
    DRF_STANDARDIZED_ERRORS = {"ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True}
    debug_toolbar_enabled = not IS_RUNNING_TESTS and is_optional_module_available("debug_toolbar")

    extend_enabled_items(
        INSTALLED_APPS,
        (debug_toolbar_enabled, "debug_toolbar"),
    )

    extend_enabled_items(
        MIDDLEWARE,
        (
            is_optional_module_available("whitenoise"),
            "whitenoise.middleware.WhiteNoiseMiddleware",
        ),
        (
            debug_toolbar_enabled,
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ),
        (
            is_optional_module_available("query_counter"),
            "query_counter.middleware.DjangoQueryCounterMiddleware",
        ),
        (
            is_optional_module_available("querycount"),
            "querycount.middleware.QueryCountMiddleware",
        ),
    )

    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 100,
        "DEFAULT_RENDERER_CLASSES": (
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ),
        "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }
else:
    REST_FRAMEWORK = {
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": 100,
        "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
        "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }

# Настройки мониторинга запросов.
QUERYCOUNT = {
    "THRESHOLDS": {"MEDIUM": 50, "HIGH": 200, "MIN_TIME_TO_LOG": 0, "MIN_QUERY_COUNT_TO_LOG": 0},
    "IGNORE_REQUEST_PATTERNS": [],
    "IGNORE_SQL_PATTERNS": [],
    "DISPLAY_DUPLICATES": None,
    "RESPONSE_HEADER": "X-DjangoQueryCount-Count",
}

# Логирование.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "json_file": {
            "class": "logging.handlers.WatchedFileHandler",
            "filename": str(LOGS_DIR / "json.log"),
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["json_file", "console"],
            "level": "INFO",
        },
        "django": {"level": "ERROR", "handlers": ["console"]},
    },
}

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Настройки CORS.
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", cast=bool, default=True)
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv(), default="")

DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda _request: DEBUG}

if config("USE_HTTPS", cast=bool, default=False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [
        "^health/",
    ]
    SECURE_REDIRECT_EXEMPT += config("SECURE_REDIRECT_EXEMPT", cast=Csv())


REDIS_URL = config("REDIS_URL", default="redis://127.0.0.1:6379/1")
POST_CACHE_TIMEOUT = config("POST_CACHE_TIMEOUT", cast=int, default=300)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}

# Настройки Swagger и ReDoc.
# Берём метаданные прямо из Poetry, чтобы не дублировать их в settings.py.
with (BASE_DIR / "pyproject.toml").open("rb") as f:
    project_meta = tomllib.load(f).get("project", {})

SPECTACULAR_SETTINGS = {
    "TITLE": project_meta.get("name", "Blog API"),
    "DESCRIPTION": project_meta.get("description", ""),
    "VERSION": project_meta.get("version", ""),
    "COMPONENT_SPLIT_REQUEST": True,
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": [
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.IsAdminUser",
    ],
    "SERVE_AUTHENTICATION": [
        "rest_framework.authentication.BasicAuthentication",
    ],
    "SWAGGER_UI_SETTINGS": {
        "displayRequestDuration": True,
        "deepLinking": True,
    },
}
