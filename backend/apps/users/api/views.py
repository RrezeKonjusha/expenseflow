from django.db.models import Count
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.core.permissions import IsAdmin, IsAdminOrReadOnly

from .. import selectors, services
from ..models import Project, User
from .serializers import DepartmentSerializer, ProjectMembersSerializer, ProjectSerializer, UserSerializer


class UserFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = ["role", "department", "is_active"]


@extend_schema_view(
    list=extend_schema(tags=["Users"]),
    retrieve=extend_schema(tags=["Users"]),
    create=extend_schema(tags=["Users"]),
    update=extend_schema(tags=["Users"]),
    partial_update=extend_schema(tags=["Users"]),
    destroy=extend_schema(tags=["Users"], description="Deactivates the user (soft delete)."),
)
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "date_joined", "role"]

    def get_queryset(self):
        return selectors.users_list()

    def perform_create(self, serializer):
        serializer.instance = services.create_user(
            by=self.request.user, request=self.request, **serializer.validated_data
        )

    def perform_update(self, serializer):
        serializer.instance = services.update_user(
            serializer.instance, by=self.request.user, request=self.request, **serializer.validated_data
        )

    def perform_destroy(self, instance):
        services.deactivate_user(instance, by=self.request.user, request=self.request)


@extend_schema_view(
    list=extend_schema(tags=["Departments"]),
    retrieve=extend_schema(tags=["Departments"]),
    create=extend_schema(tags=["Departments"]),
    update=extend_schema(tags=["Departments"]),
    partial_update=extend_schema(tags=["Departments"]),
    destroy=extend_schema(tags=["Departments"]),
)
class DepartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = DepartmentSerializer
    pagination_class = None

    def get_queryset(self):
        return selectors.departments_list().annotate(member_count=Count("members"))


@extend_schema_view(
    list=extend_schema(tags=["Projects"]),
    retrieve=extend_schema(tags=["Projects"]),
    create=extend_schema(tags=["Projects"]),
    update=extend_schema(tags=["Projects"]),
    partial_update=extend_schema(tags=["Projects"]),
    destroy=extend_schema(tags=["Projects"]),
)
class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProjectSerializer
    pagination_class = None
    filterset_fields = ["is_active"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # OpenAPI schema generation
            return Project.objects.none()
        return selectors.projects_visible_to(self.request.user).prefetch_related("memberships")

    @extend_schema(tags=["Projects"], request=ProjectMembersSerializer, responses=ProjectSerializer)
    @action(detail=True, methods=["put"], permission_classes=[IsAdmin])
    def members(self, request, pk=None):
        project = self.get_object()
        ser = ProjectMembersSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        services.set_project_members(project, ser.validated_data["user_ids"], by=request.user, request=request)
        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)
