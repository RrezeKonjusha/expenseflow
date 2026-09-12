"""Expense use cases. Every state change: one transaction, one audit entry."""

import csv
import io
import json

from django.core.cache import cache
from django.db import IntegrityError, connection, transaction
from rest_framework.exceptions import PermissionDenied

from apps.core import audit
from apps.core.exceptions import BudgetExceeded, PolicyViolation
from apps.users.selectors import is_project_member

from .models import EXPENSE_CLASSES, Expense
from .selectors import can_decide

DASHBOARD_VERSION_KEY = "dashboard:version"


def bump_dashboard_cache():
    """Invalidate every cached dashboard by moving to a new key version."""
    try:
        cache.incr(DASHBOARD_VERSION_KEY)
    except ValueError:
        cache.set(DASHBOARD_VERSION_KEY, 2, None)


def _require_owner(expense: Expense, user):
    if expense.employee_id != user.pk:
        raise PermissionDenied("Only the owner can do this.")


@transaction.atomic
def create_expense(*, user, data: dict, request=None) -> Expense:
    data = dict(data)
    cls = EXPENSE_CLASSES[data.pop("type")]
    expense = cls(employee=user, **data)
    expense.ensure_policy(is_member=is_project_member(user.pk, expense.project_id))
    expense.save()
    audit.record("EXPENSE_CREATED", actor=user, target=("Expense", expense.pk), request=request)
    return expense


@transaction.atomic
def update_expense(expense: Expense, *, user, data: dict, request=None) -> Expense:
    _require_owner(expense, user)
    if not expense.is_editable:
        raise PolicyViolation("Only draft expenses can be edited.")
    changes = {}
    for key, value in data.items():
        if key == "type":
            continue
        old = getattr(expense, key)
        if old != value:
            changes[key] = (getattr(old, "pk", old), getattr(value, "pk", value))
            setattr(expense, key, value)
    expense.ensure_policy(is_member=is_project_member(user.pk, expense.project_id))
    expense.save()
    if changes:
        audit.record("EXPENSE_UPDATED", actor=user, target=("Expense", expense.pk), changes=changes, request=request)
    return expense


@transaction.atomic
def delete_expense(expense: Expense, *, user, request=None) -> None:
    _require_owner(expense, user)
    if not expense.is_editable:
        raise PolicyViolation("Only draft expenses can be deleted.")
    pk = expense.pk
    expense.delete()
    audit.record("EXPENSE_DELETED", actor=user, target=("Expense", pk), request=request)


def _transition(expense, user, action, request, mutate, extra_changes=None):
    old = expense.status
    mutate()
    try:
        with transaction.atomic():
            expense.save()
    except IntegrityError as exc:
        if "project_spent_within_budget" in str(exc):
            raise BudgetExceeded(
                f"Project {expense.project.code} budget would be exceeded "
                f"(budget {expense.project.budget}, spent {expense.project.spent}, this expense {expense.amount})."
            ) from exc
        raise
    changes = {"status": (old, expense.status), **(extra_changes or {})}
    audit.record(f"EXPENSE_{action}", actor=user, target=("Expense", expense.pk), changes=changes, request=request)
    bump_dashboard_cache()
    return expense


def submit_expense(expense, *, user, request=None):
    _require_owner(expense, user)
    member = is_project_member(user.pk, expense.project_id)
    return _transition(expense, user, "SUBMITTED", request, lambda: expense.submit(is_member=member))


def approve_expense(expense, *, user, request=None):
    if not can_decide(user, expense):
        raise PermissionDenied("Only the department manager or an admin can approve this expense.")
    return _transition(expense, user, "APPROVED", request, lambda: expense.approve(user))


def reject_expense(expense, *, user, reason: str, request=None):
    if not can_decide(user, expense):
        raise PermissionDenied("Only the department manager or an admin can reject this expense.")
    return _transition(
        expense, user, "REJECTED", request, lambda: expense.reject(user, reason), {"rejection_reason": ("", reason)}
    )


def reopen_expense(expense, *, user, request=None):
    _require_owner(expense, user)
    return _transition(expense, user, "REOPENED", request, expense.reopen)


def reimburse_until(*, user, until, request=None) -> int:
    """Calls the PL/pgSQL stored procedure sp_mark_reimbursed."""
    with transaction.atomic(), connection.cursor() as cur:
        cur.execute("SELECT sp_mark_reimbursed(%s)", [until])
        count = cur.fetchone()[0]
    audit.record(
        "EXPENSES_REIMBURSED",
        actor=user,
        target=("Batch", str(until)),
        changes={"count": (0, count)},
        request=request,
    )
    bump_dashboard_cache()
    return count


# ---- import (extra feature 10) ---------------------------------------------------------

IMPORT_COLUMNS = [
    "type",
    "project_code",
    "amount",
    "expense_date",
    "description",
    "distance_km",
    "destination",
    "attendees",
    "item_name",
    "serial_no",
]
MAX_IMPORT_ROWS = 500


def parse_import_file(uploaded) -> list[dict]:
    raw = uploaded.read()
    if len(raw) > 2 * 1024 * 1024:
        raise PolicyViolation("File is larger than 2 MB.")
    text = raw.decode("utf-8-sig")
    name = (uploaded.name or "").lower()
    if name.endswith(".json"):
        rows = json.loads(text)
        if not isinstance(rows, list):
            raise PolicyViolation("JSON import must be a list of objects.")
    else:
        rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) > MAX_IMPORT_ROWS:
        raise PolicyViolation(f"At most {MAX_IMPORT_ROWS} rows per import.")
    return [{k: (v if v not in ("", None) else None) for k, v in r.items() if k in IMPORT_COLUMNS} for r in rows]


def import_expenses(*, user, rows: list[dict], serializer_class, request=None) -> dict:
    """Validate every row; create valid rows as DRAFT; report errors per row (1-based, header excluded)."""
    from apps.users.models import Project

    created, errors = [], []
    projects = {p.code: p.pk for p in Project.objects.filter(is_active=True)}
    for i, row in enumerate(rows, start=1):
        row = {k: v for k, v in row.items() if v is not None}
        code = row.pop("project_code", None)
        if code not in projects:
            errors.append({"row": i, "errors": {"project_code": [f"Unknown project '{code}'."]}})
            continue
        row["project"] = projects[code]
        ser = serializer_class(data=row, context={"request": request})
        if not ser.is_valid():
            errors.append({"row": i, "errors": ser.errors})
            continue
        try:
            with transaction.atomic():
                exp = create_expense(user=user, data=ser.validated_data, request=request)
            created.append(exp.pk)
        except PolicyViolation as exc:
            errors.append({"row": i, "errors": exc.errors})
    audit.record(
        "EXPENSES_IMPORTED",
        actor=user,
        target=("Import", len(rows)),
        changes={"created": (0, len(created)), "failed": (0, len(errors))},
        request=request,
    )
    return {"created": len(created), "created_ids": created, "errors": errors}
