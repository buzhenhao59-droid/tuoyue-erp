from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.products.views import (
    ProductCategoryViewSet, ProductViewSet, ProductSKUViewSet, ProductPlatformMappingViewSet
)

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet, basename='product-category')
router.register(r'items', ProductViewSet, basename='product')
router.register(r'skus', ProductSKUViewSet, basename='product-sku')
router.register(r'platform-mappings', ProductPlatformMappingViewSet, basename='platform-mapping')

urlpatterns = [
    path('', include(router.urls)),
]
