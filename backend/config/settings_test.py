"""Settings for pytest: same as production except fast, in-process backing services.

Set TEST_MONGO_URL and TEST_REDIS_URL (CI does) to run the whole suite against real MongoDB and Redis
instead of mongomock and the in-memory cache; tests marked `real_services` only run in that mode.
"""

import os

from .settings import *  # noqa: F401,F403

DEBUG = False
TEST_REDIS_URL = os.environ.get("TEST_REDIS_URL")
TEST_MONGO_URL = os.environ.get("TEST_MONGO_URL")
if TEST_REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": TEST_REDIS_URL,
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
MONGO_URL = TEST_MONGO_URL or "mongomock://localhost/expenseflow_test"
CELERY_TASK_ALWAYS_EAGER = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
REFRESH_COOKIE_SECURE = False
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
LOGGING = {"version": 1, "disable_existing_loggers": False}
