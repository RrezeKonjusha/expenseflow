"""Email adapter with a circuit breaker (pybreaker).

After 3 consecutive SMTP failures the breaker opens for 60 s and calls fail
fast instead of hanging every request on a dead mail server.
"""

import logging

import pybreaker
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

smtp_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60, name="smtp")


@smtp_breaker
def send_now(to: str, subject: str, body: str) -> None:
    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=False)


def send(to: str, subject: str, body: str) -> None:
    """Queue an email (or send inline when Celery runs eagerly)."""
    from ..tasks import send_email_task

    try:
        send_email_task.delay(to, subject, body)
    except pybreaker.CircuitBreakerError:
        logger.error("SMTP circuit open, email to %s not sent", to)
    except Exception:
        logger.exception("Email to %s failed", to)
