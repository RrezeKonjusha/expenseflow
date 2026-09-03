from datetime import datetime, time

from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView

from ..documents import AuditLog
from ..permissions import IsAdmin
from .serializers import AuditLogSerializer


@extend_schema(
    tags=["Audit"],
    parameters=[
        OpenApiParameter("action", str),
        OpenApiParameter("user", int, description="actor user id"),
        OpenApiParameter("date_from", str, description="YYYY-MM-DD"),
        OpenApiParameter("date_to", str, description="YYYY-MM-DD"),
    ],
)
class AuditLogListView(ListAPIView):
    """Admin: browse the audit trail stored in MongoDB."""

    permission_classes = [IsAdmin]
    serializer_class = AuditLogSerializer
    filter_backends = []

    def get_queryset(self):
        qs = AuditLog.objects
        p = self.request.query_params
        if p.get("action"):
            qs = qs.filter(action=p["action"])
        if p.get("user"):
            qs = qs.filter(actor__user_id=int(p["user"]))
        if (d := parse_date(p.get("date_from", "") or "")) is not None:
            qs = qs.filter(ts__gte=make_aware(datetime.combine(d, time.min)))
        if (d := parse_date(p.get("date_to", "") or "")) is not None:
            qs = qs.filter(ts__lte=make_aware(datetime.combine(d, time.max)))
        return qs.order_by("-ts")
