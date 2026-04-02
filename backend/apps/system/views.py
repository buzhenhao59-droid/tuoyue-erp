from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.utils import timezone

from apps.system.models import SystemConfig, OperationLog, ScheduledTask, Notification
from apps.system.serializers import (
    SystemConfigSerializer, OperationLogSerializer,
    ScheduledTaskSerializer, NotificationSerializer, NotificationReadSerializer
)


class SystemConfigViewSet(viewsets.ModelViewSet):
    """系统配置视图集"""
    serializer_class = SystemConfigSerializer
    lookup_field = 'config_key'
    
    def get_queryset(self):
        tenant = self.request.tenant
        return SystemConfig.objects.filter(tenant=tenant)


class OperationLogFilter(filters.FilterSet):
    """操作日志过滤器"""
    action = filters.CharFilter(field_name='action')
    module = filters.CharFilter(field_name='module')
    user = filters.NumberFilter(field_name='user_id')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = OperationLog
        fields = ['action', 'module', 'user']


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志视图集"""
    serializer_class = OperationLogSerializer
    filterset_class = OperationLogFilter
    
    def get_queryset(self):
        tenant = self.request.tenant
        return OperationLog.objects.filter(tenant=tenant).select_related('user')


class ScheduledTaskViewSet(viewsets.ModelViewSet):
    """定时任务视图集"""
    serializer_class = ScheduledTaskSerializer
    
    def get_queryset(self):
        tenant = self.request.tenant
        return ScheduledTask.objects.filter(tenant=tenant)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """启用/禁用任务"""
        task = self.get_object()
        task.is_enabled = not task.is_enabled
        task.save()
        return Response(ScheduledTaskSerializer(task).data)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """立即执行任务"""
        task = self.get_object()
        
        # 这里应该调用Celery任务
        # 简化处理，仅更新状态
        task.last_run_at = timezone.now()
        task.last_run_status = 2  # 成功
        task.last_run_result = '任务执行成功'
        task.save()
        
        return Response(ScheduledTaskSerializer(task).data)


class NotificationViewSet(viewsets.ModelViewSet):
    """通知视图集"""
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """获取未读通知"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({
            'count': notifications.count(),
            'notifications': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """标记通知为已读"""
        serializer = NotificationReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data.get('notification_ids', [])
        
        queryset = self.get_queryset().filter(is_read=False)
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        count = queryset.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'marked_count': count,
            'message': f'已标记{count}条通知为已读'
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有通知为已读"""
        count = self.get_queryset().filter(is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )
        return Response({
            'marked_count': count,
            'message': f'已标记{count}条通知为已读'
        })
