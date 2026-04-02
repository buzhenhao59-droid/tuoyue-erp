"""
拓岳 ERP - Dashboard URL 配置
"""

from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('sales-trend/', views.sales_trend, name='sales-trend'),
    path('order-distribution/', views.order_distribution, name='order-distribution'),
    path('top-products/', views.top_products, name='top-products'),
]