from django.urls import path
from .dashboard_views import DashboardStatsView, DashboardChartView, InventoryAlertView

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/chart/', DashboardChartView.as_view(), name='dashboard-chart'),
    path('dashboard/inventory-alert/', InventoryAlertView.as_view(), name='inventory-alert'),
]
