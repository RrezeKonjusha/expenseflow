from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.core.permissions import IsAdmin

from .. import selectors, services
from ..filters import ExpenseFilter
from ..models import Expense
from .serializers import (
    ExpenseSerializer,
    ImportResultSerializer,
    ImportSerializer,
    ReimburseSerializer,
    RejectSerializer,
)

TAG = ["Expenses"]


@extend_schema_view(
    list=extend_schema(tags=TAG),
    retrieve=extend_schema(tags=TAG),
    create=extend_schema(tags=TAG),
    update=extend_schema(tags=TAG),
    partial_update=extend_schema(tags=TAG),
    destroy=extend_schema(tags=TAG),
)
class ExpenseViewSet(viewsets.ModelViewSet):
    """Expenses visible to the caller (own, department, or all by role)."""

    serializer_class = ExpenseSerializer
    filterset_class = ExpenseFilter
    ordering_fields = ["expense_date", "amount", "status", "created_at"]
    ordering = ["-expense_date", "-id"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # OpenAPI schema generation
            return Expense.objects.none()
        return selectors.expenses_visible_to(self.request.user)

    def perform_create(self, serializer):
        serializer.instance = services.create_expense(
            user=self.request.user, data=serializer.validated_data, request=self.request
        )

    def perform_update(self, serializer):
        serializer.instance = services.update_expense(
            serializer.instance, user=self.request.user, data=serializer.validated_data, request=self.request
        )

    def perform_destroy(self, instance):
        services.delete_expense(instance, user=self.request.user, request=self.request)

    def _respond(self, expense):
        return Response(self.get_serializer(expense).data)

    @extend_schema(tags=TAG, request=None, summary="DRAFT -> SUBMITTED (owner)")
    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        return self._respond(services.submit_expense(self.get_object(), user=request.user, request=request))

    @extend_schema(tags=TAG, request=None, summary="SUBMITTED -> APPROVED (manager of department, admin)")
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._respond(services.approve_expense(self.get_object(), user=request.user, request=request))

    @extend_schema(tags=TAG, request=RejectSerializer, summary="SUBMITTED -> REJECTED (reason required)")
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        ser = RejectSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        expense = services.reject_expense(
            self.get_object(), user=request.user, reason=ser.validated_data["reason"], request=request
        )
        return self._respond(expense)

    @extend_schema(tags=TAG, request=None, summary="REJECTED -> DRAFT (owner)")
    @action(detail=True, methods=["post"])
    def reopen(self, request, pk=None):
        return self._respond(services.reopen_expense(self.get_object(), user=request.user, request=request))

    @extend_schema(
        tags=TAG,
        request=ReimburseSerializer,
        responses={200: {"type": "object", "properties": {"reimbursed": {"type": "integer"}}}},
        summary="Admin: mark APPROVED expenses up to a date as REIMBURSED (stored procedure)",
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAdmin])
    def reimburse(self, request):
        ser = ReimburseSerializer(data=request.data or {"until": timezone.localdate()})
        ser.is_valid(raise_exception=True)
        count = services.reimburse_until(user=request.user, until=ser.validated_data["until"], request=request)
        return Response({"reimbursed": count})

    @extend_schema(
        tags=TAG,
        request={"multipart/form-data": ImportSerializer},
        responses={200: ImportResultSerializer},
        summary="Import expenses from CSV or JSON as drafts; returns per-row errors",
    )
    @action(detail=False, methods=["post"], url_path="import", parser_classes=[MultiPartParser, FormParser, JSONParser])
    def import_file(self, request):
        ser = ImportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        rows = services.parse_import_file(ser.validated_data["file"])
        result = services.import_expenses(
            user=request.user, rows=rows, serializer_class=ExpenseSerializer, request=request
        )
        return Response(result, status=status.HTTP_200_OK)
