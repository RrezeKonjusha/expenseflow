import pytest

from apps.core.documents import AuditLog
from apps.users.models import User

pytestmark = pytest.mark.django_db


def test_admin_user_crud(world):
    c = world.client(world.admin)
    r = c.post(
        "/api/v1/users/",
        {"email": "Neo@test.dev", "password": "Sup3r-Secret-1", "role": "MANAGER", "department": world.eng.pk},
    )
    assert r.status_code == 201, r.data
    uid = r.data["id"]
    assert r.data["email"] == "neo@test.dev" and "password" not in r.data
    assert c.get("/api/v1/users/", {"role": "MANAGER"}).data["count"] == 3
    assert c.get("/api/v1/users/", {"search": "neo"}).data["count"] == 1
    assert c.patch(f"/api/v1/users/{uid}/", {"role": "USER"}).data["role"] == "USER"
    assert c.delete(f"/api/v1/users/{uid}/").status_code == 204
    assert not User.objects.get(pk=uid).is_active
    assert AuditLog.objects(action="USER_UPDATED").count() == 1


def test_create_user_requires_password(world):
    r = world.client(world.admin).post("/api/v1/users/", {"email": "p@test.dev"})
    assert r.status_code == 400 and "password" in r.data["errors"]


def test_departments(world):
    admin = world.client(world.admin)
    r = admin.post("/api/v1/departments/", {"name": "Finance", "manager": world.besa.pk})
    assert r.status_code == 201
    assert admin.post("/api/v1/departments/", {"name": "finance"}).status_code == 400
    assert admin.post("/api/v1/departments/", {"name": "HR", "manager": world.arta.pk}).status_code == 400
    assert len(world.client(world.arta).get("/api/v1/departments/").data) == 3
    assert world.client(world.arta).post("/api/v1/departments/", {"name": "X"}).status_code == 403


def test_projects_and_members(world):
    admin = world.client(world.admin)
    r = admin.post("/api/v1/projects/", {"code": "NEW-1", "name": "New", "budget": "500"})
    assert r.status_code == 201
    pid = r.data["id"]
    assert admin.post("/api/v1/projects/", {"code": "lower", "name": "x", "budget": "1"}).status_code == 400
    r = admin.put(f"/api/v1/projects/{pid}/members/", {"user_ids": [world.arta.pk, world.arta.pk]}, format="json")
    assert r.status_code == 200 and r.data["member_ids"] == [world.arta.pk]
    assert admin.put(f"/api/v1/projects/{pid}/members/", {"user_ids": [99999]}, format="json").status_code == 400
    codes = [p["code"] for p in world.client(world.arta).get("/api/v1/projects/").data]
    assert sorted(codes) == ["ALPHA", "NEW-1", "TIGHT"]
    assert [p["code"] for p in world.client(world.driton).get("/api/v1/projects/").data] == []


def test_budget_cannot_go_below_spent(world):
    world.alpha.spent = 500
    world.alpha.save()
    r = world.client(world.admin).patch(f"/api/v1/projects/{world.alpha.pk}/", {"budget": "100"})
    assert r.status_code == 400


def test_audit_log_endpoint(world):
    admin = world.client(world.admin)
    admin.post("/api/v1/departments/", {"name": "Ops"})
    admin.patch(f"/api/v1/users/{world.arta.pk}/", {"first_name": "Arta2"})
    r = admin.get("/api/v1/audit-logs/", {"action": "USER_UPDATED"})
    assert r.status_code == 200 and r.data["count"] == 1
    entry = r.data["results"][0]
    assert entry["actor"]["email"] == "admin@test.dev"
    assert entry["changes"][0]["field"] == "first_name"
    assert admin.get("/api/v1/audit-logs/", {"user": world.admin.pk, "date_from": "2020-01-01"}).data["count"] == 1


def test_health(api, db):
    r = api.get("/health/")
    assert r.status_code == 200 and r.json()["checks"]["postgres"] == "ok"
