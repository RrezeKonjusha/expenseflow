from rest_framework.routers import SimpleRouter

from .views import DepartmentViewSet, ProjectViewSet, UserViewSet

router = SimpleRouter()
router.register("users", UserViewSet, basename="user")
router.register("departments", DepartmentViewSet, basename="department")
router.register("projects", ProjectViewSet, basename="project")

urlpatterns = router.urls
