"""Audit trail service: one call per critical action, written to MongoDB.

Writes go through Celery when a worker runs (CELERY_TASK_ALWAYS_EAGER=False),
so auditing never slows down or breaks the user's request.
"""

import logging

from .logging import request_id_var

logger = logging.getLogger(__name__)


def _client_ip(request):
    if request is None:
        return None
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    return fwd.split(",")[0].strip() if fwd else request.META.get("REMOTE_ADDR")


def record(action, *, actor=None, target=None, changes=None, request=None):
    """Record an audit event.

    actor   -- a User (or None for anonymous/system)
    target  -- a model instance or a (type, id) tuple
    changes -- dict {field: (old, new)}
    """
    payload = {
        "action": action,
        "actor": (
            {"user_id": actor.pk, "email": actor.email, "role": actor.role}
            if actor is not None and getattr(actor, "pk", None)
            else None
        ),
        "target": None,
        "changes": [{"field": f, "old": _plain(o), "new": _plain(n)} for f, (o, n) in (changes or {}).items()],
        "ip": _client_ip(request),
        "request_id": request_id_var.get(),
    }
    if target is not None:
        if isinstance(target, tuple):
            payload["target"] = {"type": target[0], "id": str(target[1])}
        else:
            payload["target"] = {"type": type(target).__name__, "id": str(target.pk)}

    from .tasks import write_audit

    try:
        write_audit.delay(payload)
    except Exception:  # broker down: never fail the business action
        logger.exception("Could not queue audit event %s", action)
        write_audit(payload)


def _plain(value):
    if value is None or isinstance(value, (int, float, bool, str)):
        return value
    return str(value)
