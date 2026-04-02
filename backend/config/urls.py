"""Tuoyue ERP URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/tenants/', include('apps.tenants.urls')),
    path('api/v1/platforms/', include('apps.platforms.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/collections/', include('apps.collections.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/suppliers/', include('apps.suppliers.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/logistics/', include('apps.logistics.urls')),
    path('api/v1/system/', include('apps.system.urls')),
    path('api/v1/dashboard/', include('apps.dashboard.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
