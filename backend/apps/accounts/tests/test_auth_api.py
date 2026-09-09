"""Auth module: registration, activation, login, refresh rotation, logout, passwords."""

import re

import pytest
from django.conf import settings
from django.core import mail

from apps.core.documents import AuditLog
from apps.users.models import User
from tests.factories import PASSWORD, UserFactory

pytestmark = pytest.mark.django_db
A = "/api/v1/auth/"
COOKIE = settings.REFRESH_COOKIE_NAME


def _link_parts(body, kind):
    m = re.search(rf"/{kind}/([^/]+)/([^/\s]+)", body)
    return {"uid": m.group(1), "token": m.group(2)}


def login(api, email, password=PASSWORD):
    return api.post(f"{A}login/", {"email": email, "password": password})


def test_register_activate_login(api):
    r = api.post(f"{A}register/", {"email": "New@Test.dev", "password": PASSWORD, "first_name": "Nora"})
    assert r.status_code == 201
    user = User.objects.get(email="new@test.dev")
    assert not user.is_active and len(mail.outbox) == 1
    assert login(api, "new@test.dev").status_code == 401  # not active yet
    parts = _link_parts(mail.outbox[0].body, "activate")
    assert api.post(f"{A}activate/", parts).status_code == 200
    assert api.post(f"{A}activate/", parts).status_code == 400  # single use
    r = login(api, "new@test.dev")
    assert r.status_code == 200 and r.data["access"] and r.data["user"]["role"] == "USER"
    cookie = r.cookies[COOKIE]
    assert cookie["httponly"] and cookie["samesite"] == "Strict" and cookie["path"] == "/api/v1/auth/"
    assert AuditLog.objects(action="LOGIN").count() == 1


def test_register_duplicate_and_weak_password(api, db):
    UserFactory(email="taken@test.dev")
    assert api.post(f"{A}register/", {"email": "taken@test.dev", "password": PASSWORD}).status_code == 400
    assert api.post(f"{A}register/", {"email": "x@test.dev", "password": "1234567890"}).status_code == 400


def test_refresh_rotation_and_reuse_detection(api, db):
    UserFactory(email="r@test.dev")
    login(api, "r@test.dev")
    old = api.cookies[COOKIE].value
    r = api.post(f"{A}refresh/")
    assert r.status_code == 200 and r.data["access"]
    assert api.cookies[COOKIE].value != old  # rotated
    api.cookies[COOKIE] = old
    assert api.post(f"{A}refresh/").status_code == 401  # old token blacklisted


def test_refresh_without_cookie(api, db):
    assert api.post(f"{A}refresh/").status_code == 401


def test_logout_blacklists(api, db):
    UserFactory(email="l@test.dev")
    login(api, "l@test.dev")
    token = api.cookies[COOKIE].value
    assert api.post(f"{A}logout/").status_code == 204
    api.cookies[COOKIE] = token
    assert api.post(f"{A}refresh/").status_code == 401


def test_me_get_and_patch(api, db):
    UserFactory(email="me@test.dev")
    access = login(api, "me@test.dev").data["access"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    assert api.get(f"{A}me/").data["email"] == "me@test.dev"
    r = api.patch(f"{A}me/", {"first_name": "Era", "role": "ADMIN"})
    assert r.data["first_name"] == "Era" and r.data["role"] == "USER"  # role is read-only


def test_change_password_revokes_sessions(api, db):
    UserFactory(email="c@test.dev")
    access = login(api, "c@test.dev").data["access"]
    api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    assert (
        api.post(f"{A}password/change/", {"current_password": "wrong", "new_password": "N3w-Pass-2026"}).status_code
        == 400
    )
    assert (
        api.post(f"{A}password/change/", {"current_password": PASSWORD, "new_password": "N3w-Pass-2026"}).status_code
        == 200
    )
    assert api.post(f"{A}refresh/").status_code == 401
    api.credentials()
    assert login(api, "c@test.dev", "N3w-Pass-2026").status_code == 200


def test_forgot_and_reset(api, db):
    UserFactory(email="f@test.dev")
    assert api.post(f"{A}password/forgot/", {"email": "nobody@test.dev"}).status_code == 200
    assert len(mail.outbox) == 0  # no enumeration, no email
    assert api.post(f"{A}password/forgot/", {"email": "f@test.dev"}).status_code == 200
    parts = _link_parts(mail.outbox[0].body, "reset-password")
    assert api.post(f"{A}password/reset/", {**parts, "new_password": "Brand-New-77"}).status_code == 200
    assert api.post(f"{A}password/reset/", {**parts, "new_password": "Brand-New-78"}).status_code == 400
    assert login(api, "f@test.dev", "Brand-New-77").status_code == 200


def test_activation_bad_uid(api, db):
    assert api.post(f"{A}activate/", {"uid": "zzz", "token": "x"}).status_code == 400
