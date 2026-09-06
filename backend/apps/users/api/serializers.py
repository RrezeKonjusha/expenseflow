import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..models import Department, Project, Role, User

NO_HTML = re.compile(r"[<>]")


def no_html(value: str) -> str:
    if NO_HTML.search(value or ""):
        raise serializers.ValidationError("HTML characters < and > are not allowed.")
    return value


class DepartmentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, validators=[no_html])
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, validators=[no_html])

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "department",
            "department_name",
            "is_active",
            "date_joined",
            "last_login",
            "password",
        ]
        read_only_fields = ["date_joined", "last_login"]

    def validate_email(self, value):
        return value.lower()

    def validate(self, attrs):
        pwd = attrs.get("password")
        if self.instance is None and not pwd:
            raise serializers.ValidationError({"password": "Required when creating a user."})
        if pwd:
            validate_password(pwd)
        return attrs


class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role"]


class DepartmentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, validators=[no_html])
    manager_name = serializers.CharField(source="manager.full_name", read_only=True, default=None)
    member_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Department
        fields = ["id", "name", "manager", "manager_name", "member_count", "created_at"]
        read_only_fields = ["created_at"]

    def validate_manager(self, manager):
        if manager and manager.role not in (Role.MANAGER, Role.ADMIN):
            raise serializers.ValidationError("Manager must have the MANAGER or ADMIN role.")
        return manager

    def validate_name(self, value):
        qs = Department.objects.filter(name__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A department with this name already exists.")
        return value


class ProjectSerializer(serializers.ModelSerializer):
    code = serializers.RegexField(r"^[A-Z0-9-]{2,20}$", help_text="Uppercase letters, digits, dash")
    name = serializers.CharField(max_length=150, validators=[no_html])
    budget = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    member_ids = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "code", "name", "budget", "spent", "is_active", "member_ids", "created_at"]
        read_only_fields = ["spent", "created_at"]

    def get_member_ids(self, obj) -> list[int]:
        return list(obj.memberships.values_list("user_id", flat=True))

    def validate(self, attrs):
        budget = attrs.get("budget")
        if self.instance and budget is not None and budget < self.instance.spent:
            raise serializers.ValidationError({"budget": "Budget cannot be lower than the amount already spent."})
        return attrs


class ProjectMembersSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=True)

    def validate_user_ids(self, ids):
        found = set(User.objects.filter(pk__in=ids).values_list("pk", flat=True))
        missing = set(ids) - found
        if missing:
            raise serializers.ValidationError(f"Unknown user ids: {sorted(missing)}")
        return list(dict.fromkeys(ids))
