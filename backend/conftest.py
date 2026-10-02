import pytest
from django.conf import settings
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.documents import AuditLog
from apps.reporting.documents import ReportSnapshot
from tests.factories import DepartmentFactory, ProjectFactory, UserFactory


def pytest_collection_modifyitems(config, items):
    if settings.TEST_MONGO_URL and settings.TEST_REDIS_URL:
        return
    skip = pytest.mark.skip(reason="needs TEST_MONGO_URL and TEST_REDIS_URL (real MongoDB and Redis)")
    for item in items:
        if "real_services" in item.keywords:
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def _clean_state():
    cache.clear()
    AuditLog.drop_collection()
    ReportSnapshot.drop_collection()
    yield


@pytest.fixture
def api():
    return APIClient()


def auth_client(user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(user).access_token}")
    return client


@pytest.fixture
def world(db):
    """Two departments, a manager each, employees, an admin and two projects."""
    eng = DepartmentFactory(name="Engineering")
    sales = DepartmentFactory(name="Sales")
    admin = UserFactory(role="ADMIN", email="admin@test.dev")
    besa = UserFactory(role="MANAGER", department=eng, email="besa@test.dev")
    driton = UserFactory(role="MANAGER", department=sales, email="driton@test.dev")
    arta = UserFactory(department=eng, email="arta@test.dev")
    blerim = UserFactory(department=sales, email="blerim@test.dev")
    eng.manager, sales.manager = besa, driton
    eng.save()
    sales.save()
    alpha = ProjectFactory(code="ALPHA", budget=10000, members=[arta, blerim, besa])
    tight = ProjectFactory(code="TIGHT", budget=100, members=[arta])
    return type(
        "World",
        (),
        dict(
            eng=eng,
            sales=sales,
            admin=admin,
            besa=besa,
            driton=driton,
            arta=arta,
            blerim=blerim,
            alpha=alpha,
            tight=tight,
            client=staticmethod(auth_client),
        ),
    )
