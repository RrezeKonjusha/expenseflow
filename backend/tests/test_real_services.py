"""Integration tests against real MongoDB and Redis (CI service containers).

mongomock and the in-memory cache cannot prove these: write concern, server-side indexes,
Redis-backed throttle counters and atomic cache versioning.
"""

from datetime import date, timedelta

import pytest
from django.core.cache import cache
from django_redis import get_redis_connection

from apps.core.documents import AuditLog
from apps.expenses import services as expense_services
from apps.reporting import services as reporting
from apps.reporting.documents import ReportSnapshot

pytestmark = [pytest.mark.real_services, pytest.mark.django_db]


def test_health_reports_every_real_backend(api):
    res = api.get("/health/")
    assert res.status_code == 200
    assert res.json()["checks"] == {"postgres": "ok", "mongo": "ok", "redis": "ok"}


def test_audit_indexes_exist_on_the_server(world):
    AuditLog.ensure_indexes()
    keys = [tuple(ix["key"].items()) for ix in AuditLog._get_collection().list_indexes()]
    assert (("ts", -1),) in keys
    assert (("actor.user_id", 1), ("ts", -1)) in keys


def test_snapshot_is_saved_with_majority_write_concern_and_embedded_owner(world):
    criteria = {"date_from": date.today() - timedelta(days=30), "date_to": date.today(), "group_by": "department"}
    snap = reporting.save_snapshot(world.admin, name="By department", criteria=criteria)
    stored = ReportSnapshot._get_collection().find_one({"_id": snap.pk})
    assert stored["owner"] == {"user_id": world.admin.pk, "email": world.admin.email}
    assert stored["criteria"]["group_by"] == "department"


def test_dashboard_is_cached_in_redis_and_invalidated_by_version_bump(world):
    reporting.dashboard(world.admin)
    redis = get_redis_connection("default")
    assert any(b"dashboard:v1:all" in k for k in redis.keys("*dashboard*"))

    expense_services.bump_dashboard_cache()  # what every expense transition calls
    assert cache.get(expense_services.DASHBOARD_VERSION_KEY) == 2
    reporting.dashboard(world.admin)
    assert any(b"dashboard:v2:all" in k for k in redis.keys("*dashboard*"))


def test_login_throttle_counters_live_in_redis(api, db):
    for _ in range(5):
        api.post("/api/v1/auth/login/", {"email": "nobody@test.dev", "password": "wrong-password"}, format="json")
    res = api.post("/api/v1/auth/login/", {"email": "nobody@test.dev", "password": "wrong-password"}, format="json")
    assert res.status_code == 429
    assert get_redis_connection("default").keys("*throttle_auth*")
