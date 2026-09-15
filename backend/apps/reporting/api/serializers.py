from rest_framework import serializers

from apps.expenses.models import ExpenseStatus, ExpenseType
from apps.users.api.serializers import no_html

from ..services import GROUPS


class CriteriaSerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()
    group_by = serializers.ChoiceField(choices=sorted(GROUPS))
    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=ExpenseStatus.choices), required=False, default=list
    )
    types = serializers.ListField(
        child=serializers.ChoiceField(choices=ExpenseType.choices), required=False, default=list
    )
    department_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)
    project_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), required=False, default=list)

    def validate(self, attrs):
        if attrs["date_from"] > attrs["date_to"]:
            raise serializers.ValidationError({"date_to": "Must be on or after date_from."})
        if (attrs["date_to"] - attrs["date_from"]).days > 3 * 366:
            raise serializers.ValidationError({"date_to": "Reports can span at most 3 years."})
        return attrs


class RowSerializer(serializers.Serializer):
    key = serializers.CharField()
    label = serializers.CharField()
    count = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)


class TotalsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=14, decimal_places=2)


class ReportResultSerializer(serializers.Serializer):
    criteria = CriteriaSerializer()
    rows = RowSerializer(many=True)
    totals = TotalsSerializer()


class SaveReportSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120, validators=[no_html])
    criteria = CriteriaSerializer()


class SnapshotSerializer(serializers.Serializer):
    id = serializers.CharField(source="pk", read_only=True)
    name = serializers.CharField()
    owner = serializers.SerializerMethodField()
    scope = serializers.CharField()
    criteria = serializers.SerializerMethodField()
    rows = RowSerializer(many=True)
    totals = TotalsSerializer()
    generated_at = serializers.DateTimeField()

    def get_owner(self, obj) -> dict:
        return {"user_id": obj.owner.user_id, "email": obj.owner.email}

    def get_criteria(self, obj) -> dict:
        c = obj.criteria
        return {
            "date_from": c.date_from,
            "date_to": c.date_to,
            "group_by": c.group_by,
            "statuses": c.statuses,
            "types": c.types,
            "department_ids": c.department_ids,
            "project_ids": c.project_ids,
        }


class DashboardSerializer(serializers.Serializer):
    scope = serializers.CharField()
    counts = serializers.DictField(child=serializers.IntegerField())
    spent_this_month = serializers.DecimalField(max_digits=14, decimal_places=2)
    pending_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    monthly = serializers.ListField(child=serializers.DictField())
    by_type = serializers.ListField(child=serializers.DictField())
    generated_at = serializers.DateTimeField()
