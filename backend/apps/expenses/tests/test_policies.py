"""Unit tests for the pure policy functions (no database)."""

from datetime import date, timedelta
from decimal import Decimal as D

from apps.expenses import policies as p

TODAY = date(2026, 9, 30)


def test_common_ok():
    assert p.common_violations(expense_date=TODAY, today=TODAY, is_member=True) == {}


def test_future_date_rejected():
    errors = p.common_violations(expense_date=TODAY + timedelta(days=1), today=TODAY, is_member=True)
    assert "expense_date" in errors


def test_too_old_rejected():
    errors = p.common_violations(expense_date=TODAY - timedelta(days=91), today=TODAY, is_member=True)
    assert "expense_date" in errors


def test_edge_exactly_90_days_ok():
    assert p.common_violations(expense_date=TODAY - timedelta(days=90), today=TODAY, is_member=True) == {}


def test_non_member_rejected():
    assert "project" in p.common_violations(expense_date=TODAY, today=TODAY, is_member=False)


def test_travel_cap():
    assert p.travel_violations(amount=D("40.00"), distance_km=D("100")) == {}
    assert "amount" in p.travel_violations(amount=D("40.01"), distance_km=D("100"))
    assert "distance_km" in p.travel_violations(amount=D("1"), distance_km=None)


def test_meal_cap_per_attendee():
    assert p.meal_violations(amount=D("50.00"), attendees=2) == {}
    assert "amount" in p.meal_violations(amount=D("60.00"), attendees=2)
    assert "attendees" in p.meal_violations(amount=D("10"), attendees=0)


def test_equipment_rules():
    assert p.equipment_violations(amount=D("1000.00"), serial_no="X") == {}
    errors = p.equipment_violations(amount=D("1000.01"), serial_no=" ")
    assert set(errors) == {"amount", "serial_no"}


def test_merge():
    assert p.merge({"a": ["1"]}, {"a": ["2"], "b": ["3"]}) == {"a": ["1", "2"], "b": ["3"]}
