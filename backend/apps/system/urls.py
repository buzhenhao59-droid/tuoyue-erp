from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 简化system模块，只保留基础URL
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
