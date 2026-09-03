import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(ignore_result=True)
def write_audit(payload: dict):
    from .documents import Actor, AuditLog, Change, Target

    try:
        AuditLog(
            action=payload["action"],
            actor=Actor(**payload["actor"]) if payload.get("actor") else None,
            target=Target(**payload["target"]) if payload.get("target") else None,
            changes=[Change(**c) for c in payload.get("changes", [])],
            ip=payload.get("ip"),
            request_id=payload.get("request_id"),
        ).save()
    except Exception:
        logger.exception("Audit write failed for %s", payload.get("action"))


@shared_task(ignore_result=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_email_task(to: str, subject: str, body: str):
    from .integrations.email import send_now

    send_now(to, subject, body)
