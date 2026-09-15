from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.DashboardView.as_view(), name="report-dashboard"),
    path("run/", views.RunReportView.as_view(), name="report-run"),
    path("", views.SnapshotListView.as_view(), name="report-list"),
    path("<str:pk>/", views.SnapshotDetailView.as_view(), name="report-detail"),
    path("<str:pk>/export/", views.SnapshotExportView.as_view(), name="report-export"),
]
