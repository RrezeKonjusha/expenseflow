from rest_framework import serializers


class AuditLogSerializer(serializers.Serializer):
    id = serializers.CharField(source="pk")
    ts = serializers.DateTimeField()
    action = serializers.CharField()
    actor = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()
    changes = serializers.SerializerMethodField()
    ip = serializers.CharField(allow_null=True)
    request_id = serializers.CharField(allow_null=True)

    def get_actor(self, obj) -> dict | None:
        return obj.actor.to_mongo().to_dict() if obj.actor else None

    def get_target(self, obj) -> dict | None:
        return obj.target.to_mongo().to_dict() if obj.target else None

    def get_changes(self, obj) -> list[dict]:
        return [c.to_mongo().to_dict() for c in obj.changes]
