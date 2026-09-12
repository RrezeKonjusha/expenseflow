"""One serializer for all expense types. The `type` field picks the subtype fields."""

from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.users.api.serializers import no_html
from apps.users.models import Project

from ..models import EXPENSE_CLASSES, Expense, ExpenseType
from ..selectors import allowed_actions

LINK_METHODS = {
    "update": ("expense-detail", "PATCH"),
    "delete": ("expense-detail", "DELETE"),
    "submit": ("expense-submit", "POST"),
    "approve": ("expense-approve", "POST"),
    "reject": ("expense-reject", "POST"),
    "reopen": ("expense-reopen", "POST"),
}


class ExpenseSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(choices=ExpenseType.choices)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.filter(is_active=True))
    project_code = serializers.CharField(source="project.code", read_only=True)
    employee = serializers.IntegerField(source="employee_id", read_only=True)
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    department_name = serializers.CharField(source="employee.department.name", read_only=True, default=None)
    decided_by_name = serializers.CharField(source="decided_by.full_name", read_only=True, default=None)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    description = serializers.CharField(max_length=500, validators=[no_html])
    reimbursable_amount = serializers.SerializerMethodField()
    # subtype fields: optional at this level, required per type in validate()
    distance_km = serializers.DecimalField(max_digits=8, decimal_places=1, min_value=Decimal("0.1"), required=False)
    destination = serializers.CharField(max_length=150, required=False, validators=[no_html])
    attendees = serializers.IntegerField(min_value=1, max_value=500, required=False)
    item_name = serializers.CharField(max_length=150, required=False, validators=[no_html])
    serial_no = serializers.CharField(max_length=100, required=False, allow_blank=True, validators=[no_html])
    _links = serializers.SerializerMethodField()

    class Meta:
        model = Expense
        fields = [
            "id",
            "type",
            "status",
            "amount",
            "currency",
            "expense_date",
            "description",
            "project",
            "project_code",
            "employee",
            "employee_name",
            "department_name",
            "distance_km",
            "destination",
            "attendees",
            "item_name",
            "serial_no",
            "reimbursable_amount",
            "submitted_at",
            "decided_by",
            "decided_by_name",
            "decided_at",
            "rejection_reason",
            "reimbursed_at",
            "created_at",
            "updated_at",
            "_links",
        ]
        read_only_fields = [
            "status",
            "currency",
            "submitted_at",
            "decided_by",
            "decided_at",
            "rejection_reason",
            "reimbursed_at",
            "created_at",
            "updated_at",
        ]

    def validate_expense_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError("Expense date cannot be in the future.")
        return value

    def validate(self, attrs):
        if self.instance is not None:
            if "type" in attrs and attrs["type"] != self.instance.type:
                raise serializers.ValidationError({"type": "The type of an expense cannot change."})
            expense_type = self.instance.type
        else:
            expense_type = attrs.get("type")
        cls = EXPENSE_CLASSES[expense_type]
        missing = {}
        for field in cls.SUBTYPE_FIELDS:
            present = field in attrs or (self.instance is not None and getattr(self.instance, field, None) is not None)
            if not present:
                missing[field] = ["This field is required for this expense type."]
        if missing:
            raise serializers.ValidationError(missing)
        # drop fields that belong to other subtypes
        others = {f for c in EXPENSE_CLASSES.values() for f in c.SUBTYPE_FIELDS} - set(cls.SUBTYPE_FIELDS)
        return {k: v for k, v in attrs.items() if k not in others}

    @extend_schema_field(serializers.DecimalField(max_digits=10, decimal_places=2))
    def get_reimbursable_amount(self, obj):
        return str(obj.reimbursable_amount())

    @extend_schema_field(
        {
            "type": "object",
            "additionalProperties": {
                "type": "object",
                "properties": {"href": {"type": "string"}, "method": {"type": "string"}},
            },
        }
    )
    def get__links(self, obj):
        request = self.context.get("request")
        links = {"self": {"href": reverse("expense-detail", args=[obj.pk]), "method": "GET"}}
        if request is None or not request.user.is_authenticated:
            return links
        for act in allowed_actions(request.user, obj):
            name, method = LINK_METHODS[act]
            links[act] = {"href": reverse(name, args=[obj.pk]), "method": method}
        return links


class RejectSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=1000, validators=[no_html])


class ReimburseSerializer(serializers.Serializer):
    until = serializers.DateField()


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class ImportResultSerializer(serializers.Serializer):
    created = serializers.IntegerField()
    created_ids = serializers.ListField(child=serializers.IntegerField())
    errors = serializers.ListField(child=serializers.DictField())
