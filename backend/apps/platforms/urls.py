from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.platforms.views import PlatformViewSet, ShopViewSet

router = DefaultRouter()
router.register(r'platforms', PlatformViewSet, basename='platform')
router.register(r'shops', ShopViewSet, basename='shop')

urlpatterns = [
    path('', include(router.urls)),
]
