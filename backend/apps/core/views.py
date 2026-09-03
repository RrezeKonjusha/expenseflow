"""GET /health/ : checks PostgreSQL, MongoDB and Redis. 200 when all are up, else 503."""

from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from mongoengine.connection import get_db


def _check(fn):
    try:
        fn()
        return "ok"
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc.__class__.__name__}"


def _postgres():
    with connection.cursor() as cur:
        cur.execute("SELECT 1")


def _mongo():
    get_db().command("ping")


def _redis():
    cache.set("health:ping", "1", 5)
    if cache.get("health:ping") != "1":
        raise RuntimeError("cache read failed")


def health(request):
    checks = {"postgres": _check(_postgres), "mongo": _check(_mongo), "redis": _check(_redis)}
    ok = all(v == "ok" for v in checks.values())
    return JsonResponse({"status": "ok" if ok else "degraded", "checks": checks}, status=200 if ok else 503)
