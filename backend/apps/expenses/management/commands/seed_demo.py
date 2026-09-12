"""python manage.py seed_demo [--reset]

Creates the demo dataset used in the live demo and by Cypress:
3 departments, 1 admin, 2 managers, 6 employees, 4 projects (GAMMA at ~95% of budget),
~150 expenses over the last 6 months in every status, and one saved report.
All demo users share the password Demo-Pass-2026!
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.utils import timezone

from apps.expenses.models import EquipmentExpense, Expense, ExpenseStatus, MealExpense, TravelExpense
from apps.users.models import Department, Project, ProjectMember, Role, User

PASSWORD = "Demo-Pass-2026!"
DOMAIN = "expenseflow.dev"

PEOPLE = [
    # email, first, last, role, department
    ("admin", "Ardian", "Hoxha", Role.ADMIN, "Finance"),
    ("besa", "Besa", "Gashi", Role.MANAGER, "Engineering"),
    ("driton", "Driton", "Berisha", Role.MANAGER, "Sales"),
    ("arta", "Arta", "Krasniqi", Role.USER, "Engineering"),
    ("leon", "Leon", "Morina", Role.USER, "Engineering"),
    ("vjosa", "Vjosa", "Shala", Role.USER, "Engineering"),
    ("blerim", "Blerim", "Kelmendi", Role.USER, "Sales"),
    ("rina", "Rina", "Bytyqi", Role.USER, "Sales"),
    ("ilir", "Ilir", "Rexhepi", Role.USER, "Finance"),
]

PROJECTS = [
    ("ALPHA", "Customer portal", Decimal("20000")),
    ("BETA", "Sales expansion Albania", Decimal("15000")),
    ("GAMMA", "Office equipment refresh", Decimal("3000")),
    ("DELTA", "Partner conference", Decimal("8000")),
]

MEALS = [
    "Lunch with client at Hotel Sirius",
    "Team dinner after release",
    "Coffee with supplier",
    "Business lunch in Tirana",
]
TRIPS = [("Prizren", 160), ("Tirana", 500), ("Skopje", 180), ("Peja", 170), ("Airport", 40)]
ITEMS = [("Monitor 27in", 280), ("Keyboard", 60), ("Docking station", 190), ("Headset", 90), ("Laptop stand", 45)]


class Command(BaseCommand):
    help = "Seed demo data (idempotent with --reset)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete existing expenses, projects and users first")

    @transaction.atomic
    def handle(self, *args, **opts):
        rnd = random.Random(42)
        if opts["reset"]:
            Expense.objects.all().delete()
            ProjectMember.objects.all().delete()
            Project.objects.all().delete()
            User.objects.filter(email__endswith=f"@{DOMAIN}").delete()
            Department.objects.all().delete()

        depts = {n: Department.objects.get_or_create(name=n)[0] for n in ("Engineering", "Sales", "Finance")}
        users = {}
        for key, first, last, role, dept in PEOPLE:
            u, created = User.objects.get_or_create(
                email=f"{key}@{DOMAIN}",
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "role": role,
                    "department": depts[dept],
                    "is_active": True,
                },
            )
            if created:
                u.set_password(PASSWORD)
                if role == Role.ADMIN:
                    u.is_staff = u.is_superuser = True
                u.save()
            users[key] = u
        depts["Engineering"].manager = users["besa"]
        depts["Sales"].manager = users["driton"]
        depts["Finance"].manager = users["admin"]
        for d in depts.values():
            d.save()

        projects = {}
        for code, name, budget in PROJECTS:
            projects[code], _ = Project.objects.get_or_create(code=code, defaults={"name": name, "budget": budget})
        everyone = [u for k, u in users.items() if k != "admin"]
        for p in projects.values():
            for u in everyone:
                ProjectMember.objects.get_or_create(project=p, user=u)

        if Expense.objects.exists():
            self.stdout.write(self.style.WARNING("Expenses already exist; use --reset to rebuild."))
            return

        today = timezone.localdate()
        now = timezone.now()
        employees = [users[k] for k in ("arta", "leon", "vjosa", "blerim", "rina", "ilir", "besa", "driton")]
        approver = {"Engineering": users["besa"], "Sales": users["driton"], "Finance": users["admin"]}
        created = 0
        for _ in range(150):
            emp = rnd.choice(employees)
            age = rnd.randint(0, 175)
            date = today - timedelta(days=age)
            project = projects[rnd.choice(["ALPHA", "ALPHA", "BETA", "DELTA"])]
            kind = rnd.choice(["MEAL", "MEAL", "TRAVEL", "EQUIPMENT"])
            if kind == "MEAL":
                att = rnd.randint(1, 4)
                exp = MealExpense(
                    attendees=att, amount=Decimal(rnd.randint(8, 25 * att)), description=rnd.choice(MEALS)
                )
            elif kind == "TRAVEL":
                dest, km = rnd.choice(TRIPS)
                exp = TravelExpense(
                    destination=dest,
                    distance_km=Decimal(km),
                    amount=Decimal(int(km * 0.4) - rnd.randint(0, 10)),
                    description=f"Car trip to {dest}",
                )
            else:
                item, price = rnd.choice(ITEMS)
                exp = EquipmentExpense(
                    item_name=item, serial_no=f"SN-{rnd.randint(10000, 99999)}", amount=Decimal(price), description=item
                )
            exp.employee, exp.project, exp.expense_date = emp, project, date
            # older expenses are further along the workflow
            if age > 60:
                status = rnd.choice([ExpenseStatus.REIMBURSED] * 3 + [ExpenseStatus.REJECTED])
            elif age > 14:
                status = rnd.choice(
                    [ExpenseStatus.APPROVED, ExpenseStatus.APPROVED, ExpenseStatus.REJECTED, ExpenseStatus.SUBMITTED]
                )
            else:
                status = rnd.choice([ExpenseStatus.DRAFT, ExpenseStatus.SUBMITTED, ExpenseStatus.SUBMITTED])
            exp.status = status
            if status != ExpenseStatus.DRAFT:
                exp.submitted_at = now - timedelta(days=max(age - 1, 0))
            if status in (ExpenseStatus.APPROVED, ExpenseStatus.REJECTED, ExpenseStatus.REIMBURSED):
                dec = approver[emp.department.name]
                exp.decided_by = users["admin"] if dec == emp else dec
                exp.decided_at = now - timedelta(days=max(age - 2, 0))
            if status == ExpenseStatus.REJECTED:
                exp.rejection_reason = rnd.choice(["Receipt missing", "Not project related", "Above policy limit"])
            if status == ExpenseStatus.REIMBURSED:
                exp.reimbursed_at = now - timedelta(days=max(age - 5, 0))
            exp.save()
            created += 1

        # GAMMA: nearly exhausted budget so the live demo can show the trigger blocking an approval
        gamma = projects["GAMMA"]
        for i, (item, price) in enumerate([("Laptop", 1000), ("Laptop", 1000), ("Laptop", 850)]):
            EquipmentExpense.objects.create(
                employee=users["vjosa"],
                project=gamma,
                item_name=item,
                serial_no=f"GM-{i}",
                amount=Decimal(price),
                description=f"{item} for new hire",
                expense_date=today - timedelta(days=20 + i),
                status=ExpenseStatus.APPROVED,
                submitted_at=now,
                decided_by=users["besa"],
                decided_at=now,
            )
        EquipmentExpense.objects.create(
            employee=users["arta"],
            project=gamma,
            item_name="Docking station",
            serial_no="GM-9",
            amount=Decimal("190"),
            description="Docking station for hot desk",
            expense_date=today - timedelta(days=3),
            status=ExpenseStatus.SUBMITTED,
            submitted_at=now,
        )

        # rows inserted as APPROVED/REIMBURSED never fired the UPDATE trigger: recompute spent once
        with connection.cursor() as cur:
            cur.execute(
                """
                UPDATE users_project p SET spent = COALESCE((
                    SELECT SUM(e.amount) FROM expenses_expense e
                    WHERE e.project_id = p.id AND e.status IN ('APPROVED', 'REIMBURSED')), 0)
                """
            )
            cur.execute("UPDATE users_project SET budget = GREATEST(budget, spent + 500) WHERE code <> 'GAMMA'")

        self._saved_report(users["admin"])
        self.stdout.write(self.style.SUCCESS(f"Seeded {created + 4} expenses. Log in with any *@{DOMAIN} / {PASSWORD}"))

    def _saved_report(self, admin):
        from apps.reporting.documents import ReportSnapshot
        from apps.reporting.services import save_snapshot

        try:
            ReportSnapshot.objects(name="Last 90 days by department").delete()
            today = timezone.localdate()
            save_snapshot(
                admin,
                name="Last 90 days by department",
                criteria={
                    "date_from": today - timedelta(days=90),
                    "date_to": today,
                    "group_by": "department",
                    "statuses": ["APPROVED", "REIMBURSED"],
                    "types": [],
                    "department_ids": [],
                    "project_ids": [],
                },
            )
        except Exception as exc:  # noqa: BLE001 - Mongo is optional for the SQL seed
            self.stdout.write(
                self.style.WARNING(f"Saved report skipped (MongoDB unavailable: {exc.__class__.__name__})")
            )
