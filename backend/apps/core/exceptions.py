"""Domain errors and the single API error format: {type, detail, errors}."""

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Base class for business-rule failures raised by services and models."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "domain_error"

    def __init__(self, detail: str, errors: dict | None = None):
        super().__init__(detail)
        self.detail = detail
        self.errors = errors or {}


class PolicyViolation(DomainError):
    code = "policy_violation"


class InvalidTransition(DomainError):
    status_code = status.HTTP_409_CONFLICT
    code = "invalid_transition"


class BudgetExceeded(DomainError):
    status_code = status.HTTP_409_CONFLICT
    code = "budget_exceeded"


def _body(type_: str, detail: str, errors=None):
    return {"type": type_, "detail": detail, "errors": errors or {}}


def api_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        return Response(_body(exc.code, exc.detail, exc.errors), status=exc.status_code)
    if isinstance(exc, DjangoValidationError):
        errors = exc.message_dict if hasattr(exc, "error_dict") else {"non_field_errors": exc.messages}
        return Response(_body("validation_error", "Invalid input.", errors), status=400)
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    if isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, context)
    if response is None:
        logger.exception("Unhandled error", exc_info=exc)
        return None
    if isinstance(exc, exceptions.ValidationError):
        errors = response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
        response.data = _body("validation_error", "Invalid input.", errors)
    else:
        detail = response.data.get("detail", str(exc)) if isinstance(response.data, dict) else str(exc)
        response.data = _body(getattr(exc, "default_code", "error"), str(detail))
    return response
