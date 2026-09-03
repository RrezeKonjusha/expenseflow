"""MongoDB documents for the audit trail (embedded actor, target, changes)."""

from datetime import UTC, datetime

from mongoengine import (
    DateTimeField,
    Document,
    DynamicField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
    ListField,
    StringField,
)


def utcnow():
    return datetime.now(UTC)


class Actor(EmbeddedDocument):
    user_id = IntField()
    email = StringField()
    role = StringField()


class Target(EmbeddedDocument):
    type = StringField()
    id = StringField()


class Change(EmbeddedDocument):
    field = StringField(required=True)
    old = DynamicField()
    new = DynamicField()


class AuditLog(Document):
    ts = DateTimeField(default=utcnow, required=True)
    action = StringField(required=True, max_length=64)
    actor = EmbeddedDocumentField(Actor)
    target = EmbeddedDocumentField(Target)
    changes = ListField(EmbeddedDocumentField(Change))
    ip = StringField()
    request_id = StringField()

    meta = {
        "collection": "audit_logs",
        "ordering": ["-ts"],
        "indexes": ["-ts", ("actor.user_id", "-ts"), "action"],
    }
