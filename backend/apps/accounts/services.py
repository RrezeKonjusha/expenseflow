"""Authentication use cases: registration, activation, password flows, logout."""

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core import audit
from apps.core.exceptions import DomainError
from apps.core.integrations import email
from apps.users.models import User

from .tokens import activation_token, decode_uid, encode_uid, password_reset_token


class InvalidToken(DomainError):
    code = "invalid_token"


def _link(path: str) -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}{path}"


@transaction.atomic
def register(*, email_address: str, password: str, first_name="", last_name="", request=None) -> User:
    user = User(email=email_address.lower(), first_name=first_name, last_name=last_name, is_active=False)
    validate_password(password, user)
    user.set_password(password)
    user.save()
    url = _link(f"/activate/{encode_uid(user)}/{activation_token.make_token(user)}")
    email.send(
        user.email,
        "Activate your ExpenseFlow account",
        f"Hi {user.first_name or user.email},\n\nActivate your account: {url}\n\nThe link is valid for 3 days.",
    )
    audit.record("USER_REGISTERED", actor=user, target=user, request=request)
    return user


def _user_from_uid(uid: str) -> User:
    pk = decode_uid(uid)
    user = User.objects.filter(pk=pk).first() if pk else None
    if user is None:
        raise InvalidToken("The link is invalid or has expired.")
    return user


def activate(*, uid: str, token: str, request=None) -> User:
    user = _user_from_uid(uid)
    if not activation_token.check_token(user, token):
        raise InvalidToken("The link is invalid or has expired.")
    user.is_active = True
    user.save(update_fields=["is_active"])
    audit.record("USER_ACTIVATED", actor=user, target=user, request=request)
    return user


def request_password_reset(*, email_address: str, request=None) -> None:
    """Always succeeds silently so attackers cannot discover registered emails."""
    user = User.objects.filter(email__iexact=email_address, is_active=True).first()
    if not user:
        return
    url = _link(f"/reset-password/{encode_uid(user)}/{password_reset_token.make_token(user)}")
    email.send(
        user.email,
        "Reset your ExpenseFlow password",
        f"Reset your password: {url}\n\nIgnore this email if you did not ask.",
    )
    audit.record("PASSWORD_RESET_REQUESTED", actor=user, target=user, request=request)


@transaction.atomic
def reset_password(*, uid: str, token: str, new_password: str, request=None) -> None:
    user = _user_from_uid(uid)
    if not password_reset_token.check_token(user, token):
        raise InvalidToken("The link is invalid or has expired.")
    validate_password(new_password, user)
    user.set_password(new_password)
    user.save(update_fields=["password"])
    revoke_all_refresh_tokens(user)
    audit.record("PASSWORD_RESET", actor=user, target=user, request=request)


@transaction.atomic
def change_password(user: User, *, current_password: str, new_password: str, request=None) -> None:
    if not user.check_password(current_password):
        raise DomainError("Current password is incorrect.", {"current_password": ["Incorrect password."]})
    validate_password(new_password, user)
    user.set_password(new_password)
    user.save(update_fields=["password"])
    revoke_all_refresh_tokens(user)
    audit.record("PASSWORD_CHANGED", actor=user, target=user, request=request)


def revoke_all_refresh_tokens(user: User) -> None:
    """Log the user out everywhere (used after password change or reset)."""
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


def logout(*, refresh: str | None, request=None) -> None:
    """Blacklist the refresh token so it can never mint access tokens again."""
    if not refresh:
        return
    try:
        token = RefreshToken(refresh)
    except TokenError:  # expired or tampered: nothing to revoke
        return
    user = User.objects.filter(pk=token.get("user_id")).first()
    token.blacklist()
    audit.record("LOGOUT", actor=user, target=user, request=request)
