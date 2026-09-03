from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import health

api_v1 = [
    path("auth/", include("apps.accounts.api.urls")),
    path("", include("apps.users.api.urls")),
    path("", include("apps.expenses.api.urls")),
    path("reports/", include("apps.reporting.api.urls")),
    path("", include("apps.core.api.urls")),
]

urlpatterns = [
    path("api/v1/", include(api_v1)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("", include("django_prometheus.urls")),  # /metrics (not exposed by Caddy)
]
