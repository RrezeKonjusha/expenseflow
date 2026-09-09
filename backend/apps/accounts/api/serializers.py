from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.api.serializers import no_html
from apps.users.models import User


class LoginSerializer(TokenObtainPairSerializer):
    """Adds role, department and email to the JWT claims."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["department_id"] = user.department_id
        token["email"] = user.email
        return token


class MeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, validators=[no_html])
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, validators=[no_html])

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "department", "department_name"]
        read_only_fields = ["id", "email", "role", "department"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=10)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, validators=[no_html])
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, validators=[no_html])

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()


class UidTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()


class ResetPasswordSerializer(UidTokenSerializer):
    new_password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value, self.context["request"].user)
        return value


class AccessSerializer(serializers.Serializer):
    access = serializers.CharField()
    user = MeSerializer()
