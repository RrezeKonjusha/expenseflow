"""Security suite (Faza IV): SQLi, XSS, brute force, authN/authZ."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from tests.factories import PASSWORD, MealFactory, UserFactory

pytestmark = [pytest.mark.django_db, pytest.mark.security]


def test_sql_injection_in_search_is_harmless(world):
    MealFactory(employee=world.arta, project=world.alpha)
    c = world.client(world.arta)
    for payload in ["' OR 1=1 --", "'; DROP TABLE users_user; --", '" OR ""="']:
        r = c.get("/api/v1/expenses/", {"q": payload})
        assert r.status_code == 200 and r.data["count"] == 0


def test_xss_rejected_in_text_fields(world):
    r = world.client(world.arta).post(
        "/api/v1/expenses/",
        {
            "type": "MEAL",
            "project": world.alpha.pk,
            "amount": "10",
            "attendees": 1,
            "expense_date": str(timezone.localdate() - timedelta(days=1)),
            "description": "<script>alert(1)</script>",
        },
    )
    assert r.status_code == 400 and "description" in r.data["errors"]


def test_unauthenticated_is_401(api, db):
    assert api.get("/api/v1/expenses/").status_code == 401


def test_tampered_token_is_401(world):
    c = world.client(world.arta)
    token = c._credentials["HTTP_AUTHORIZATION"]
    c.credentials(HTTP_AUTHORIZATION=token[:-3] + "abc")
    assert c.get("/api/v1/expenses/").status_code == 401


def test_user_cannot_approve_own(world):
    e = MealFactory(employee=world.arta, project=world.alpha, status="SUBMITTED")
    assert world.client(world.arta).post(f"/api/v1/expenses/{e.pk}/approve/").status_code == 403


def test_manager_of_other_department_cannot_see(world):
    e = MealFactory(employee=world.arta, project=world.alpha, status="SUBMITTED")
    assert world.client(world.driton).post(f"/api/v1/expenses/{e.pk}/approve/").status_code == 404


def test_user_cannot_use_admin_endpoints(world):
    c = world.client(world.arta)
    assert c.get("/api/v1/users/").status_code == 403
    assert c.get("/api/v1/audit-logs/").status_code == 403
    assert c.post("/api/v1/projects/", {"code": "X1", "name": "x", "budget": "1"}).status_code == 403


def test_login_throttle_429(settings, db):
    UserFactory(email="t@test.dev")
    api = APIClient()
    codes = [api.post("/api/v1/auth/login/", {"email": "t@test.dev", "password": "bad"}).status_code for _ in range(6)]
    assert codes[-1] == 429


def test_account_lockout_after_5_failures(db, settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {"anon": "1000/min", "user": "1000/min", "auth": "1000/min"},
    }
    UserFactory(email="lock@test.dev")
    api = APIClient()
    for _ in range(5):
        api.post("/api/v1/auth/login/", {"email": "lock@test.dev", "password": "bad"})
    r = api.post("/api/v1/auth/login/", {"email": "lock@test.dev", "password": PASSWORD})
    assert r.status_code in (403, 429)


def test_security_headers(api, db):
    r = api.get("/health/")
    assert r["X-Content-Type-Options"] == "nosniff"
    assert r["X-Frame-Options"] == "DENY"
    assert r["X-Request-ID"]
