"""Auth endpoints. The refresh token only ever travels in an httpOnly cookie."""

from django.conf import settings
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

from apps.core import audit
from apps.users.models import User

from .. import services
from .serializers import (
    AccessSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    MeSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UidTokenSerializer,
)

DetailSerializer = inline_serializer("Detail", {"detail": serializers.CharField()})


def _set_refresh_cookie(response, refresh: str):
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        refresh,
        max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite="Strict",
        path=settings.REFRESH_COOKIE_PATH,
    )


def _clear_refresh_cookie(response):
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path=settings.REFRESH_COOKIE_PATH, samesite="Strict")


def _refresh_from(request) -> str | None:
    return request.COOKIES.get(settings.REFRESH_COOKIE_NAME) or request.data.get("refresh")


class AuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = "auth"

    def get_authenticate_header(self, request):
        # without this DRF turns failed logins into 403 because no auth class is set
        return 'Bearer realm="api"'


@extend_schema(tags=["Auth"], request=RegisterSerializer, responses={201: DetailSerializer})
class RegisterView(AuthView):
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        services.register(
            email_address=d["email"],
            password=d["password"],
            first_name=d.get("first_name", ""),
            last_name=d.get("last_name", ""),
            request=request,
        )
        return Response({"detail": "Check your email to activate the account."}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Auth"], request=UidTokenSerializer, responses={200: DetailSerializer})
class ActivateView(AuthView):
    def post(self, request):
        ser = UidTokenSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        services.activate(**ser.validated_data, request=request)
        return Response({"detail": "Account activated. You can log in now."})


@extend_schema(
    tags=["Auth"],
    request=inline_serializer("Login", {"email": serializers.EmailField(), "password": serializers.CharField()}),
    responses={200: AccessSerializer},
)
class LoginView(AuthView):
    def post(self, request):
        ser = LoginSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        user = ser.user
        audit.record("LOGIN", actor=user, target=user, request=request)
        response = Response({"access": ser.validated_data["access"], "user": MeSerializer(user).data})
        _set_refresh_cookie(response, ser.validated_data["refresh"])
        return response


@extend_schema(tags=["Auth"], request=None, responses={200: AccessSerializer})
class RefreshView(AuthView):
    throttle_scope = None

    def post(self, request):
        ser = TokenRefreshSerializer(data={"refresh": _refresh_from(request) or ""})
        try:
            ser.is_valid(raise_exception=True)
        except (TokenError, InvalidToken, serializers.ValidationError):
            response = Response(
                {"type": "token_not_valid", "detail": "Session expired. Please log in again.", "errors": {}},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            _clear_refresh_cookie(response)
            return response
        access = ser.validated_data["access"]
        user = User.objects.select_related("department").get(pk=AccessToken(access)["user_id"])
        if not user.is_active:
            return Response({"type": "inactive", "detail": "Account disabled.", "errors": {}}, status=401)
        response = Response({"access": access, "user": MeSerializer(user).data})
        _set_refresh_cookie(response, ser.validated_data["refresh"])
        return response


@extend_schema(tags=["Auth"], request=None, responses={204: None})
class LogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []  # works even when the access token already expired

    def post(self, request):
        try:
            services.logout(refresh=_refresh_from(request), request=request)
        except TokenError:
            pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        _clear_refresh_cookie(response)
        return response


@extend_schema(tags=["Auth"])
class MeView(RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch"]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        before = {k: getattr(self.request.user, k) for k in serializer.validated_data}
        serializer.save()
        changes = {k: (before[k], v) for k, v in serializer.validated_data.items() if before[k] != v}
        if changes:
            audit.record(
                "PROFILE_UPDATED",
                actor=self.request.user,
                target=self.request.user,
                changes=changes,
                request=self.request,
            )


@extend_schema(tags=["Auth"], request=ChangePasswordSerializer, responses={200: DetailSerializer})
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "auth"

    def post(self, request):
        ser = ChangePasswordSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        services.change_password(request.user, **ser.validated_data, request=request)
        return Response({"detail": "Password changed. Other sessions were signed out."})


@extend_schema(tags=["Auth"], request=ForgotPasswordSerializer, responses={200: DetailSerializer})
class ForgotPasswordView(AuthView):
    def post(self, request):
        ser = ForgotPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        services.request_password_reset(email_address=ser.validated_data["email"], request=request)
        return Response({"detail": "If the email exists, a reset link has been sent."})


@extend_schema(tags=["Auth"], request=ResetPasswordSerializer, responses={200: DetailSerializer})
class ResetPasswordView(AuthView):
    def post(self, request):
        ser = ResetPasswordSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        services.reset_password(**ser.validated_data, request=request)
        return Response({"detail": "Password updated. You can log in now."})
