"""Company expense policy. Pure functions: no database, easy to unit test.

Each returns a dict {field: [messages]}; empty means the expense complies.
"""

from datetime import date, timedelta
from decimal import Decimal

TRAVEL_RATE_PER_KM = Decimal("0.40")
MEAL_CAP_PER_ATTENDEE = Decimal("25.00")
EQUIPMENT_MAX = Decimal("1000.00")
MAX_AGE_DAYS = 90


def _add(errors: dict, field: str, msg: str) -> None:
    errors.setdefault(field, []).append(msg)


def common_violations(*, expense_date: date, today: date, is_member: bool) -> dict:
    errors: dict = {}
    if expense_date > today:
        _add(errors, "expense_date", "Expense date cannot be in the future.")
    elif expense_date < today - timedelta(days=MAX_AGE_DAYS):
        _add(errors, "expense_date", f"Expenses older than {MAX_AGE_DAYS} days cannot be claimed.")
    if not is_member:
        _add(errors, "project", "You are not a member of this project.")
    return errors


def travel_violations(*, amount: Decimal, distance_km: Decimal | None) -> dict:
    errors: dict = {}
    if not distance_km or distance_km <= 0:
        _add(errors, "distance_km", "Distance must be greater than 0.")
    elif amount > distance_km * TRAVEL_RATE_PER_KM:
        cap = (distance_km * TRAVEL_RATE_PER_KM).quantize(Decimal("0.01"))
        _add(errors, "amount", f"Travel is capped at {TRAVEL_RATE_PER_KM} EUR/km: max {cap} EUR for {distance_km} km.")
    return errors


def meal_violations(*, amount: Decimal, attendees: int | None) -> dict:
    errors: dict = {}
    if not attendees or attendees < 1:
        _add(errors, "attendees", "At least 1 attendee is required.")
    elif amount > attendees * MEAL_CAP_PER_ATTENDEE:
        cap = attendees * MEAL_CAP_PER_ATTENDEE
        _add(errors, "amount", f"Meals are capped at {MEAL_CAP_PER_ATTENDEE} EUR per attendee: max {cap} EUR.")
    return errors


def equipment_violations(*, amount: Decimal, serial_no: str | None) -> dict:
    errors: dict = {}
    if not (serial_no or "").strip():
        _add(errors, "serial_no", "Serial number is required for equipment.")
    if amount > EQUIPMENT_MAX:
        _add(errors, "amount", f"Equipment above {EQUIPMENT_MAX} EUR needs a purchase order, not an expense.")
    return errors


def merge(*dicts: dict) -> dict:
    out: dict = {}
    for d in dicts:
        for k, v in d.items():
            out.setdefault(k, []).extend(v)
    return out
