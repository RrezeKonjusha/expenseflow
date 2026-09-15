"""Saved report snapshots in MongoDB: criteria and result rows are embedded documents."""

from datetime import UTC, datetime

from mongoengine import (
    DateField,
    DateTimeField,
    DecimalField,
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    ListField,
    StringField,
)


class Owner(EmbeddedDocument):
    user_id = IntField(required=True)
    email = StringField()


class Criteria(EmbeddedDocument):
    date_from = DateField(required=True)
    date_to = DateField(required=True)
    group_by = StringField(required=True)
    statuses = ListField(StringField())
    types = ListField(StringField())
    department_ids = ListField(IntField())
    project_ids = ListField(IntField())


class Row(EmbeddedDocument):
    key = StringField()
    label = StringField()
    count = IntField()
    total = DecimalField(precision=2, force_string=True)


class Totals(EmbeddedDocument):
    count = IntField()
    total = DecimalField(precision=2, force_string=True)


class ReportSnapshot(Document):
    name = StringField(required=True, max_length=120)
    owner = EmbeddedDocumentField(Owner, required=True)
    scope = StringField()  # "all", "department:3", "user:7" at generation time (denormalized)
    criteria = EmbeddedDocumentField(Criteria, required=True)
    rows = EmbeddedDocumentListField(Row)
    totals = EmbeddedDocumentField(Totals)
    generated_at = DateTimeField(default=lambda: datetime.now(UTC))

    meta = {
        "collection": "report_snapshots",
        "ordering": ["-generated_at"],
        "indexes": [("owner.user_id", "-generated_at")],
    }
