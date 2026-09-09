from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


class ActivationTokenGenerator(PasswordResetTokenGenerator):
    """Signed, stateless token. Including is_active makes it single-use."""

    key_salt = "expenseflow.accounts.activation"

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.is_active}{timestamp}{user.email}"


activation_token = ActivationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()


def encode_uid(user) -> str:
    return urlsafe_base64_encode(force_bytes(user.pk))


def decode_uid(uid: str) -> int | None:
    try:
        return int(force_str(urlsafe_base64_decode(uid)))
    except (TypeError, ValueError, OverflowError):
        return None
