from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LogisticsCompanyViewSet, ShippingMethodViewSet

router = DefaultRouter()
router.register(r'companies', LogisticsCompanyViewSet, basename='logistics-company')
router.register(r'methods', ShippingMethodViewSet, basename='shipping-method')

urlpatterns = [
    path('', include(router.urls)),
]
