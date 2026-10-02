"""Writes demo-import.csv next to this file with dates relative to today.

Expenses older than 90 days are rejected, so regenerate the file shortly before a demo:
    python docs/demo/make_demo_import.py
Import it as arta@expenseflow.dev: 4 rows are created as drafts, row 5 breaks the meal policy (25 EUR per attendee).
"""

import csv
from datetime import date, timedelta
from pathlib import Path

COLUMNS = ["type", "project_code", "amount", "expense_date", "description",
           "distance_km", "destination", "attendees", "item_name", "serial_no"]  # fmt: skip

ROWS = [
    # type, project, amount, days ago, description, distance_km, destination, attendees, item_name, serial_no
    ("TRAVEL", "ALPHA", "36.00", 3, "Client workshop in Prizren", "120", "Prizren", "", "", ""),
    ("MEAL", "BETA", "45.00", 7, "Lunch with distributor", "", "", "2", "", ""),
    ("EQUIPMENT", "ALPHA", "89.90", 12, "USB-C hub for the meeting room", "", "", "", "USB-C hub", "HUB-2026-0117"),
    ("TRAVEL", "DELTA", "22.40", 20, "Site visit in Peja", "56", "Peja", "", "", ""),
    ("MEAL", "ALPHA", "60.00", 5, "Dinner with one guest (breaks the 25 EUR per attendee policy)", "", "", "1", "", ""),
]


def main() -> Path:
    out = Path(__file__).with_name("demo-import.csv")
    today = date.today()
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        for t, p, amount, ago, desc, km, dest, att, item, serial in ROWS:
            w.writerow([t, p, amount, (today - timedelta(days=ago)).isoformat(), desc, km, dest, att, item, serial])
    return out


if __name__ == "__main__":
    print(f"wrote {main()}")
