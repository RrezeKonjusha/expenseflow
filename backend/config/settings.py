"""Django settings for ExpenseFlow.

Every value that differs between environments comes from an environment
variable (see ../.env.example). Defaults are safe for local development.
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from environs import Env

env = Env()
env.read_env()  # reads a .env file if present

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("DJANGO_SECRET_KEY", "dev-insecure-change-me-in-production-0123456789abcdef")
DEBUG = env.bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", ["localhost", "127.0.0.1", "api"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", ["https://localhost"])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # third party
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
    "polymorphic",
    "axes",
    "django_prometheus",
    # ExpenseFlow modules
    "apps.core",
    "apps.users",
    "apps.accounts",
    "apps.expenses",
    "apps.reporting",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "apps.core.middleware.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# --- Databases -------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.parse(
        env.str("DATABASE_URL", "postgres://expenseflow:expenseflow@localhost:5432/expenseflow"),
        conn_max_age=60,
    )
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MONGO_URL = env.str("MONGO_URL", "mongodb://localhost:27017/expenseflow")
REDIS_URL = env.str("REDIS_URL", "redis://localhost:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 300,
    }
}

# --- Auth --------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# django-axes: lock an account for 15 minutes after 5 failed logins
AXES_ENABLED = env.bool("AXES_ENABLED", True)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS = ["username"]
AXES_USERNAME_FORM_FIELD = "email"
AXES_RESET_ON_SUCCESS = True
# We lock per account on purpose; per-IP abuse is handled by DRF throttles (THROTTLE_AUTH).
SILENCED_SYSTEM_CHECKS = ["axes.W006"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=env.int("JWT_ACCESS_MINUTES", 15)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=env.int("JWT_REFRESH_DAYS", 7)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "SIGNING_KEY": env.str("JWT_SIGNING_KEY", SECRET_KEY),
    "AUTH_HEADER_TYPES": ("Bearer",),
}
REFRESH_COOKIE_NAME = "ef_refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth/"
REFRESH_COOKIE_SECURE = env.bool("REFRESH_COOKIE_SECURE", True)

# --- REST framework ----------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardPagination",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env.str("THROTTLE_ANON", "60/min"),
        "user": env.str("THROTTLE_USER", "600/min"),
        "auth": env.str("THROTTLE_AUTH", "5/min"),
    },
    "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "URL_FORMAT_OVERRIDE": None,  # frees ?format= for report exports
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ExpenseFlow API",
    "DESCRIPTION": "Expense claims and approval platform (UBT Lab Course 2).",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {
        "ExpenseStatusEnum": "apps.expenses.models.ExpenseStatus",
        "ExpenseTypeEnum": "apps.expenses.models.ExpenseType",
        "RoleEnum": "apps.users.models.Role",
    },
}

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", ["http://localhost:5173"])
CORS_ALLOW_CREDENTIALS = True

# --- Security headers (Caddy adds CSP) -------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", 0)  # 31536000 in prod
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# --- Email -------------------------------------------------------------------
_email = env.dj_email_url("EMAIL_URL", "smtp://localhost:1025")
EMAIL_BACKEND = env.str("EMAIL_BACKEND", _email["EMAIL_BACKEND"])
EMAIL_HOST = _email["EMAIL_HOST"]
EMAIL_PORT = _email["EMAIL_PORT"]
EMAIL_HOST_USER = _email["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = _email["EMAIL_HOST_PASSWORD"]
EMAIL_USE_TLS = _email["EMAIL_USE_TLS"]
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", "ExpenseFlow <no-reply@expenseflow.dev>")
FRONTEND_URL = env.str("FRONTEND_URL", "https://localhost")

# --- Celery ------------------------------------------------------------------
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = None
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", True)  # False when a worker runs
CELERY_TASK_ACKS_LATE = True

# --- i18n / static -------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Belgrade"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# --- Logging: JSON lines to stdout ------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "apps.core.logging.RequestIdFilter"}},
    "formatters": {"json": {"()": "apps.core.logging.JsonFormatter"}},
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "json", "filters": ["request_id"]},
    },
    "root": {"handlers": ["console"], "level": env.str("LOG_LEVEL", "INFO")},
    "loggers": {"django.db.backends": {"level": "WARNING"}},
}

# Business settings
DASHBOARD_CACHE_SECONDS = env.int("DASHBOARD_CACHE_SECONDS", 300)  # 0 = no cache (load-test baseline)
