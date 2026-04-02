from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    CollectionConfigViewSet,
    CollectionTaskViewSet,
    CollectedProductViewSet,
    CollectionStatsViewSet,
    PluginWebhookViewSet,
    BatchImportViewSet,
    AISelectionViewSet,
)

router = DefaultRouter()
router.register(r'configs', CollectionConfigViewSet, basename='collection-config')
router.register(r'tasks', CollectionTaskViewSet, basename='collection-task')
router.register(r'products', CollectedProductViewSet, basename='collected-product')
router.register(r'stats', CollectionStatsViewSet, basename='collection-stats')
router.register(r'batch_import', BatchImportViewSet, basename='batch-import')
router.register(r'ai_select', AISelectionViewSet, basename='ai-selection')

urlpatterns = [
    path('', include(router.urls)),
    path('plugin_webhook/', PluginWebhookViewSet.as_view({'post': 'create'}), name='plugin-webhook'),
]
