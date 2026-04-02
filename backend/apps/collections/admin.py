from django.contrib import admin
from .models import CollectionConfig, CollectionTask, CollectedProduct, CollectionPluginLog


@admin.register(CollectionConfig)
class CollectionConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'tenant', 'price_rule', 'price_multiplier', 'is_default', 'created_at']
    list_filter = ['price_rule', 'is_default', 'created_at']
    search_fields = ['name', 'tenant__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CollectionTask)
class CollectionTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'task_no', 'task_type', 'tenant', 'status', 'total_count', 'success_count', 'fail_count', 'created_at']
    list_filter = ['task_type', 'status', 'source_platform', 'created_at']
    search_fields = ['task_no', 'name', 'tenant__name']
    readonly_fields = ['task_no', 'created_at']


@admin.register(CollectedProduct)
class CollectedProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'source_platform', 'source_id', 'status', 'price_min', 'price_max', 'sku_count', 'created_at']
    list_filter = ['source_platform', 'status', 'collect_status', 'created_at']
    search_fields = ['title', 'source_id', 'source_url']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CollectionPluginLog)
class CollectionPluginLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'tenant', 'plugin_id', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['plugin_id', 'tenant__name']
    readonly_fields = ['created_at', 'processed_at']
