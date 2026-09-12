"""Expense hierarchy: one abstract-like base with three concrete subtypes.

Inheritance: Expense (multi-table base) -> TravelExpense, MealExpense, EquipmentExpense.
Polymorphism: each subtype overrides `type_violations()` and `reimbursable_amount()`;
django-polymorphic makes `Expense.objects.all()` return the real subclasses.
State machine: submit / approve / reject / reopen are domain methods guarded here.
"""

from decimal import Decimal

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from django.db import models
from django.db.models import Q
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from apps.core.exceptions import InvalidTransition, PolicyViolation
from apps.core.models import BaseModel

from . import policies


class ExpenseType(models.TextChoices):
    TRAVEL = "TRAVEL", "Travel"
    MEAL = "MEAL", "Meal"
    EQUIPMENT = "EQUIPMENT", "Equipment"


class ExpenseStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"
    REIMBURSED = "REIMBURSED", "Reimbursed"


DECIDED = [ExpenseStatus.APPROVED, ExpenseStatus.REJECTED, ExpenseStatus.REIMBURSED]


class Expense(PolymorphicModel, BaseModel):
    TYPE: str = ""
    SUBTYPE_FIELDS: tuple[str, ...] = ()

    type = models.CharField(max_length=10, choices=ExpenseType.choices, editable=False)
    employee = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="expenses")
    project = models.ForeignKey("users.Project", on_delete=models.PROTECT, related_name="expenses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="EUR", db_default="EUR")
    expense_date = models.DateField()
    description = models.CharField(max_length=500)
    status = models.CharField(
        max_length=12, choices=ExpenseStatus.choices, default=ExpenseStatus.DRAFT, db_default=ExpenseStatus.DRAFT
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey(
        "users.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="decided_expenses"
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default="", db_default="")
    reimbursed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "expenses_expense"
        ordering = ["-expense_date", "-id"]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="expense_amount_positive"),
            models.CheckConstraint(condition=Q(type__in=ExpenseType.values), name="expense_type_valid"),
            models.CheckConstraint(condition=Q(status__in=ExpenseStatus.values), name="expense_status_valid"),
            models.CheckConstraint(
                condition=~Q(status=ExpenseStatus.REJECTED) | ~Q(rejection_reason=""),
                name="expense_rejection_has_reason",
            ),
            models.CheckConstraint(
                condition=~Q(status__in=DECIDED) | Q(decided_at__isnull=False),
                name="expense_decided_has_timestamp",
            ),
        ]
        indexes = [
            models.Index(fields=["status"], name="expense_status_idx"),
            models.Index(fields=["employee", "-expense_date"], name="expense_employee_date_idx"),
            models.Index(fields=["project", "status"], name="expense_project_status_idx"),
            GinIndex(SearchVector("description", config="simple"), name="expense_description_fts"),
        ]

    def __str__(self):
        return f"#{self.pk} {self.type} {self.amount} {self.status}"

    def save(self, *args, **kwargs):
        self.type = self.TYPE
        super().save(*args, **kwargs)

    # ---- polymorphic policy ------------------------------------------------------
    def type_violations(self) -> dict:
        raise NotImplementedError  # every subtype must define its own policy

    def reimbursable_amount(self) -> Decimal:
        return self.amount

    def policy_violations(self, *, is_member: bool, today=None) -> dict:
        today = today or timezone.localdate()
        common = policies.common_violations(expense_date=self.expense_date, today=today, is_member=is_member)
        return policies.merge(common, self.type_violations())

    def ensure_policy(self, *, is_member: bool) -> None:
        errors = self.policy_violations(is_member=is_member)
        if errors:
            raise PolicyViolation("The expense breaks company policy.", errors)

    # ---- state machine -----------------------------------------------------------
    def _require(self, *allowed: str, action: str):
        if self.status not in allowed:
            raise InvalidTransition(f"Cannot {action} an expense that is {self.status}.")

    @property
    def is_editable(self) -> bool:
        return self.status == ExpenseStatus.DRAFT

    def submit(self, *, is_member: bool):
        self._require(ExpenseStatus.DRAFT, action="submit")
        self.ensure_policy(is_member=is_member)
        self.status = ExpenseStatus.SUBMITTED
        self.submitted_at = timezone.now()

    def approve(self, by):
        self._require(ExpenseStatus.SUBMITTED, action="approve")
        if by.pk == self.employee_id:
            raise InvalidTransition("You cannot approve your own expense.")
        self.status = ExpenseStatus.APPROVED
        self.decided_by = by
        self.decided_at = timezone.now()

    def reject(self, by, reason: str):
        self._require(ExpenseStatus.SUBMITTED, action="reject")
        if by.pk == self.employee_id:
            raise InvalidTransition("You cannot reject your own expense.")
        if not (reason or "").strip():
            raise PolicyViolation("A rejection reason is required.", {"reason": ["This field is required."]})
        self.status = ExpenseStatus.REJECTED
        self.rejection_reason = reason.strip()
        self.decided_by = by
        self.decided_at = timezone.now()

    def reopen(self):
        self._require(ExpenseStatus.REJECTED, action="reopen")
        self.status = ExpenseStatus.DRAFT
        self.decided_by = None
        self.decided_at = None
        self.rejection_reason = ""
        self.submitted_at = None


class TravelExpense(Expense):
    TYPE = ExpenseType.TRAVEL
    SUBTYPE_FIELDS = ("distance_km", "destination")

    distance_km = models.DecimalField(max_digits=8, decimal_places=1)
    destination = models.CharField(max_length=150)

    class Meta:
        db_table = "expenses_travelexpense"
        constraints = [models.CheckConstraint(condition=Q(distance_km__gt=0), name="travel_distance_positive")]

    def type_violations(self) -> dict:
        return policies.travel_violations(amount=self.amount, distance_km=self.distance_km)


class MealExpense(Expense):
    TYPE = ExpenseType.MEAL
    SUBTYPE_FIELDS = ("attendees",)

    attendees = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "expenses_mealexpense"
        constraints = [models.CheckConstraint(condition=Q(attendees__gte=1), name="meal_attendees_min_one")]

    def type_violations(self) -> dict:
        return policies.meal_violations(amount=self.amount, attendees=self.attendees)

    def reimbursable_amount(self) -> Decimal:
        return min(self.amount, self.attendees * policies.MEAL_CAP_PER_ATTENDEE)


class EquipmentExpense(Expense):
    TYPE = ExpenseType.EQUIPMENT
    SUBTYPE_FIELDS = ("item_name", "serial_no")

    item_name = models.CharField(max_length=150)
    serial_no = models.CharField(max_length=100)

    class Meta:
        db_table = "expenses_equipmentexpense"

    def type_violations(self) -> dict:
        return policies.equipment_violations(amount=self.amount, serial_no=self.serial_no)


EXPENSE_CLASSES: dict[str, type[Expense]] = {
    ExpenseType.TRAVEL: TravelExpense,
    ExpenseType.MEAL: MealExpense,
    ExpenseType.EQUIPMENT: EquipmentExpense,
}
