from bson import ObjectId
from bson.errors import InvalidId
from django.http import Http404, HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core import audit

from .. import services
from .serializers import (
    CriteriaSerializer,
    DashboardSerializer,
    ReportResultSerializer,
    SaveReportSerializer,
    SnapshotSerializer,
)

TAG = ["Reports"]


def _get_snapshot(user, pk):
    try:
        oid = ObjectId(pk)
    except (InvalidId, TypeError) as exc:
        raise Http404 from exc
    snap = services.snapshots_visible_to(user).filter(pk=oid).first()
    if snap is None:
        raise Http404
    return snap


@extend_schema(tags=TAG, responses=DashboardSerializer)
class DashboardView(APIView):
    def get(self, request):
        return Response(services.dashboard(request.user))


@extend_schema(tags=TAG, request=CriteriaSerializer, responses=ReportResultSerializer)
class RunReportView(APIView):
    def post(self, request):
        ser = CriteriaSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        result = services.run_report(request.user, ser.validated_data)
        return Response(ReportResultSerializer(result).data)


class SnapshotListView(APIView):
    @extend_schema(tags=TAG, responses=SnapshotSerializer(many=True))
    def get(self, request):
        snaps = services.snapshots_visible_to(request.user).exclude("rows")[:100]
        return Response(
            [
                {
                    "id": str(s.pk),
                    "name": s.name,
                    "owner": {"user_id": s.owner.user_id, "email": s.owner.email},
                    "criteria": {
                        "date_from": s.criteria.date_from,
                        "date_to": s.criteria.date_to,
                        "group_by": s.criteria.group_by,
                    },
                    "totals": {"count": s.totals.count, "total": str(s.totals.total)} if s.totals else None,
                    "generated_at": s.generated_at,
                }
                for s in snaps
            ]
        )

    @extend_schema(tags=TAG, request=SaveReportSerializer, responses={201: SnapshotSerializer})
    def post(self, request):
        ser = SaveReportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        snap = services.save_snapshot(request.user, **ser.validated_data, request=request)
        return Response(SnapshotSerializer(snap).data, status=status.HTTP_201_CREATED)


class SnapshotDetailView(APIView):
    @extend_schema(tags=TAG, responses=SnapshotSerializer)
    def get(self, request, pk):
        return Response(SnapshotSerializer(_get_snapshot(request.user, pk)).data)

    @extend_schema(tags=TAG, responses={204: None})
    def delete(self, request, pk):
        snap = _get_snapshot(request.user, pk)
        snap.delete()
        audit.record("REPORT_DELETED", actor=request.user, target=("ReportSnapshot", pk), request=request)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=TAG,
    parameters=[OpenApiParameter("format", str, enum=["csv", "xlsx", "json"], default="csv")],
    responses={(200, "application/octet-stream"): bytes},
)
class SnapshotExportView(APIView):
    def get(self, request, pk):
        fmt = request.query_params.get("format", "csv")
        if fmt not in ("csv", "xlsx", "json"):
            return Response(
                {"type": "validation_error", "detail": "format must be csv, xlsx or json", "errors": {}}, status=400
            )
        snap = _get_snapshot(request.user, pk)
        body, content_type, filename = services.export_snapshot(snap, fmt)
        audit.record(
            "REPORT_EXPORTED",
            actor=request.user,
            target=("ReportSnapshot", pk),
            changes={"format": (None, fmt)},
            request=request,
        )
        resp = HttpResponse(body, content_type=content_type)
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp
