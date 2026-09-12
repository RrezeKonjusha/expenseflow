"""Domain model: polymorphism, state machine and database rules."""

from decimal import Decimal as D

import pytest
from django.db import IntegrityError, connection, transaction

from apps.core.exceptions import InvalidTransition, PolicyViolation
from apps.expenses.models import Expense, ExpenseStatus, MealExpense, TravelExpense
from tests.factories import EquipmentFactory, MealFactory, TravelFactory

pytestmark = pytest.mark.django_db


def test_polymorphic_query_returns_subclasses(world):
    MealFactory(employee=world.arta, project=world.alpha)
    TravelFactory(employee=world.arta, project=world.alpha)
    EquipmentFactory(employee=world.arta, project=world.alpha)
    kinds = sorted(type(e).__name__ for e in Expense.objects.all())
    assert kinds == ["EquipmentExpense", "MealExpense", "TravelExpense"]
    assert sorted(Expense.objects.values_list("type", flat=True)) == ["EQUIPMENT", "MEAL", "TRAVEL"]


def test_meal_reimbursable_amount_is_capped(world):
    meal = MealExpense(employee=world.arta, project=world.alpha, amount=D("80"), attendees=2)
    assert meal.reimbursable_amount() == D("50.00")


def test_base_class_has_no_policy():
    with pytest.raises(NotImplementedError):
        Expense().type_violations()


def test_full_lifecycle(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    e.submit(is_member=True)
    assert e.status == ExpenseStatus.SUBMITTED and e.submitted_at
    with pytest.raises(InvalidTransition):
        e.submit(is_member=True)
    e.reject(world.besa, "Missing receipt")
    assert e.status == ExpenseStatus.REJECTED and e.decided_by == world.besa
    e.reopen()
    assert e.status == ExpenseStatus.DRAFT and e.rejection_reason == ""
    e.submit(is_member=True)
    e.approve(world.besa)
    assert e.status == ExpenseStatus.APPROVED


def test_cannot_approve_own(world):
    e = MealFactory(employee=world.besa, project=world.alpha, status=ExpenseStatus.SUBMITTED)
    with pytest.raises(InvalidTransition):
        e.approve(world.besa)
    with pytest.raises(InvalidTransition):
        e.reject(world.besa, "x")


def test_reject_requires_reason(world):
    e = MealFactory(employee=world.arta, project=world.alpha, status=ExpenseStatus.SUBMITTED)
    with pytest.raises(PolicyViolation):
        e.reject(world.besa, "  ")


def test_submit_checks_policy(world):
    e = TravelFactory.build(employee=world.arta, project=world.alpha, amount=D("100"), distance_km=D("10"))
    with pytest.raises(PolicyViolation) as exc:
        e.submit(is_member=True)
    assert "amount" in exc.value.errors


# ---- database-level rules (constraints, triggers, procedure, cascades) ----------------------


def test_check_constraint_amount_positive(world):
    with pytest.raises(IntegrityError), transaction.atomic():
        MealFactory(employee=world.arta, project=world.alpha, amount=D("0"))


def test_check_constraint_rejected_needs_reason(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    with pytest.raises(IntegrityError), transaction.atomic(), connection.cursor() as cur:
        cur.execute("UPDATE expenses_expense SET status='REJECTED', decided_at=now() WHERE id=%s", [e.pk])


def test_db_default_status_is_draft(world):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT column_default FROM information_schema.columns "
            "WHERE table_name='expenses_expense' AND column_name='status'"
        )
        assert "DRAFT" in cur.fetchone()[0]


def test_trigger_adds_approved_amount_to_project(world):
    e = MealFactory(employee=world.arta, project=world.alpha, amount=D("40"), status=ExpenseStatus.SUBMITTED)
    e.approve(world.besa)
    e.save()
    world.alpha.refresh_from_db()
    assert world.alpha.spent == D("40.00")


def test_trigger_blocks_budget_overrun(world):
    e = TravelFactory(
        employee=world.arta, project=world.tight, amount=D("120"), distance_km=D("400"), status=ExpenseStatus.SUBMITTED
    )
    e.approve(world.besa)
    with pytest.raises(IntegrityError) as exc, transaction.atomic():
        e.save()
    assert "project_spent_within_budget" in str(exc.value)


def test_stored_procedure_reimburses(world):
    MealFactory(
        employee=world.arta,
        project=world.alpha,
        status=ExpenseStatus.APPROVED,
        decided_by=world.besa,
        decided_at="2026-01-01T00:00Z",
    )
    MealFactory(employee=world.arta, project=world.alpha)  # draft: untouched
    with connection.cursor() as cur:
        cur.execute("SELECT sp_mark_reimbursed(current_date)")
        assert cur.fetchone()[0] == 1
    assert Expense.objects.filter(status=ExpenseStatus.REIMBURSED).count() == 1


def test_subtype_row_cascades_at_db_level(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    with connection.cursor() as cur:
        cur.execute("DELETE FROM expenses_expense WHERE id=%s", [e.pk])
        cur.execute("SELECT count(*) FROM expenses_mealexpense WHERE expense_ptr_id=%s", [e.pk])
        assert cur.fetchone()[0] == 0


def test_touch_trigger_updates_timestamp(world):
    e = MealFactory(employee=world.arta, project=world.alpha)
    with connection.cursor() as cur:
        # even an explicit old value is overwritten by the BEFORE UPDATE trigger
        cur.execute("UPDATE expenses_expense SET updated_at='2000-01-01' WHERE id=%s", [e.pk])
    e.refresh_from_db()
    assert e.updated_at.year != 2000


def test_travel_constraint(world):
    with pytest.raises(IntegrityError), transaction.atomic():
        TravelExpense.objects.create(
            employee=world.arta,
            project=world.alpha,
            amount=D("1"),
            expense_date="2026-09-01",
            description="x",
            distance_km=D("0"),
            destination="x",
        )


def test_seed_demo_command(db):
    from django.core.management import call_command

    from apps.users.models import Project

    call_command("seed_demo", "--reset")
    assert Expense.objects.count() > 100
    gamma = Project.objects.get(code="GAMMA")
    assert gamma.spent == D("2850.00") and gamma.budget == D("3000.00")
    for p in Project.objects.all():
        assert p.spent <= p.budget
