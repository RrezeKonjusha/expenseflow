"""Integration tests: every expense endpoint, happy path, negative and edge cases."""

import io
from datetime import timedelta
from decimal import Decimal as D

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.core.documents import AuditLog
from apps.expenses.models import Expense, ExpenseStatus
from tests.factories import MealFactory, TravelFactory

pytestmark = pytest.mark.django_db
URL = "/api/v1/expenses/"


def recent(days=2):
    return str(timezone.localdate() - timedelta(days=days))


def meal_payload(project, **over):
    data = {
        "type": "MEAL",
        "project": project.pk,
        "amount": "48.00",
        "attendees": 2,
        "expense_date": recent(),
        "description": "Lunch with client at Hotel Sirius",
    }
    data.update(over)
    return data


def test_create_meal_and_links(world):
    c = world.client(world.arta)
    r = c.post(URL, meal_payload(world.alpha))
    assert r.status_code == 201, r.data
    assert r.data["type"] == "MEAL" and r.data["status"] == "DRAFT" and r.data["attendees"] == 2
    assert "distance_km" not in r.data
    assert set(r.data["_links"]) == {"self", "update", "delete", "submit"}
    assert AuditLog.objects(action="EXPENSE_CREATED").count() == 1


def test_create_policy_violation(world):
    r = world.client(world.arta).post(URL, meal_payload(world.alpha, amount="60.00", attendees=1))
    assert r.status_code == 400
    assert r.data["type"] == "policy_violation" and "amount" in r.data["errors"]


def test_missing_subtype_field(world):
    r = world.client(world.arta).post(URL, {**meal_payload(world.alpha), "type": "TRAVEL"})
    assert r.status_code == 400 and "distance_km" in r.data["errors"]


def test_future_date_rejected(world):
    future = str(timezone.localdate() + timedelta(days=1))
    r = world.client(world.arta).post(URL, meal_payload(world.alpha, expense_date=future))
    assert r.status_code == 400 and "expense_date" in r.data["errors"]


def test_non_member_cannot_claim(world):
    r = world.client(world.blerim).post(URL, meal_payload(world.tight))
    assert r.status_code == 400 and "project" in r.data["errors"]


def test_edit_and_delete_only_drafts(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    c = world.client(world.arta)
    assert c.patch(f"{URL}{e.pk}/", {"description": "Updated"}).status_code == 200
    e.refresh_from_db()
    assert e.description == "Updated"
    assert c.post(f"{URL}{e.pk}/submit/").status_code == 200
    assert c.patch(f"{URL}{e.pk}/", {"description": "x"}).status_code == 400
    assert c.delete(f"{URL}{e.pk}/").status_code == 400


def test_type_is_immutable(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    r = world.client(world.arta).patch(f"{URL}{e.pk}/", {"type": "TRAVEL"})
    assert r.status_code == 400


def test_delete_draft(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    assert world.client(world.arta).delete(f"{URL}{e.pk}/").status_code == 204
    assert not Expense.objects.filter(pk=e.pk).exists()


def test_workflow_submit_approve(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    assert world.client(world.arta).post(f"{URL}{e.pk}/submit/").status_code == 200
    manager = world.client(world.besa)
    detail = manager.get(f"{URL}{e.pk}/").data
    assert {"approve", "reject"} <= set(detail["_links"])
    r = manager.post(f"{URL}{e.pk}/approve/")
    assert r.status_code == 200 and r.data["status"] == "APPROVED" and r.data["decided_by_name"]
    world.alpha.refresh_from_db()
    assert world.alpha.spent == e.amount


def test_reject_and_reopen(world):
    e = MealFactory(employee=world.arta, project=world.alpha, status=ExpenseStatus.SUBMITTED)
    m = world.client(world.besa)
    assert m.post(f"{URL}{e.pk}/reject/", {}).status_code == 400
    r = m.post(f"{URL}{e.pk}/reject/", {"reason": "Receipt missing"})
    assert r.status_code == 200 and r.data["rejection_reason"] == "Receipt missing"
    r = world.client(world.arta).post(f"{URL}{e.pk}/reopen/")
    assert r.status_code == 200 and r.data["status"] == "DRAFT"


def test_invalid_transition_is_409(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    r = world.client(world.besa).post(f"{URL}{e.pk}/approve/")
    assert r.status_code == 409 and r.data["type"] == "invalid_transition"


def test_budget_exceeded_is_409(world):
    e = TravelFactory(
        employee=world.arta, project=world.tight, amount=D("120"), distance_km=D("400"), status=ExpenseStatus.SUBMITTED
    )
    r = world.client(world.besa).post(f"{URL}{e.pk}/approve/")
    assert r.status_code == 409 and r.data["type"] == "budget_exceeded"
    e.refresh_from_db()
    assert e.status == ExpenseStatus.SUBMITTED


def test_scoping_by_role(world):
    MealFactory(employee=world.arta, project=world.alpha)
    MealFactory(employee=world.blerim, project=world.alpha)
    assert world.client(world.arta).get(URL).data["count"] == 1
    assert world.client(world.besa).get(URL).data["count"] == 1  # own department only
    assert world.client(world.admin).get(URL).data["count"] == 2


def test_filters_and_search(world):
    MealFactory(employee=world.arta, project=world.alpha, description="Dinner at hotel Sirius")
    MealFactory(
        employee=world.arta, project=world.alpha, description="Coffee with supplier", status=ExpenseStatus.SUBMITTED
    )
    TravelFactory(employee=world.arta, project=world.alpha)
    c = world.client(world.arta)
    assert c.get(URL, {"q": "hotel"}).data["count"] == 1
    assert c.get(URL, {"status": "SUBMITTED"}).data["count"] == 1
    assert c.get(URL, {"type": ["MEAL", "TRAVEL"]}).data["count"] == 3
    assert c.get(URL, {"amount_min": "35"}).data["count"] == 2
    assert c.get(URL, {"ordering": "amount"}).data["results"][0]["type"] == "TRAVEL"
    assert c.get(URL, {"page_size": 1}).data["next"] is not None


def test_reimburse_admin_only(world):
    MealFactory(
        employee=world.arta,
        project=world.alpha,
        status=ExpenseStatus.APPROVED,
        decided_by=world.besa,
        decided_at=timezone.now(),
    )
    assert world.client(world.besa).post(f"{URL}reimburse/", {"until": recent(0)}).status_code == 403
    r = world.client(world.admin).post(f"{URL}reimburse/", {"until": recent(0)})
    assert r.status_code == 200 and r.data == {"reimbursed": 1}


def test_import_csv_with_row_errors(world):
    csv_text = (
        "type,project_code,amount,expense_date,description,distance_km,destination,attendees,item_name,serial_no\n"
        f"MEAL,ALPHA,40.00,{recent()},Team lunch,,,2,,\n"
        f"TRAVEL,ALPHA,20.00,{recent()},Taxi to airport,60,Airport,,,\n"
        f"EQUIPMENT,ALPHA,150.00,{recent()},Keyboard,,,,Keyboard,KB-1\n"
        f"MEAL,ALPHA,90.00,{recent()},Too expensive,,,1,,\n"
        f"MEAL,NOPE,10.00,{recent()},Unknown project,,,1,,\n"
    )
    f = SimpleUploadedFile("expenses.csv", csv_text.encode(), content_type="text/csv")
    r = world.client(world.arta).post(f"{URL}import/", {"file": f}, format="multipart")
    assert r.status_code == 200, r.data
    assert r.data["created"] == 3
    assert [e["row"] for e in r.data["errors"]] == [4, 5]


def test_import_json(world):
    body = f'[{{"type":"MEAL","project_code":"ALPHA","amount":"20","expense_date":"{recent()}","description":"x","attendees":1}}]'
    f = SimpleUploadedFile("e.json", body.encode(), content_type="application/json")
    r = world.client(world.arta).post(f"{URL}import/", {"file": f}, format="multipart")
    assert r.data["created"] == 1


def test_import_rejects_bad_json(world):
    f = SimpleUploadedFile("e.json", io.BytesIO(b'{"a": 1}').read())
    r = world.client(world.arta).post(f"{URL}import/", {"file": f}, format="multipart")
    assert r.status_code == 400
