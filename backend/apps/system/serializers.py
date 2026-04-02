from rest_framework import serializers
from apps.system.models import SystemConfig, OperationLog, ScheduledTask, Notification


class SystemConfigSerializer(serializers.ModelSerializer):
    """系统配置序列化器"""
    
    class Meta:
        model = SystemConfig
        fields = '__all__'
        read_only_fields = ['tenant']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class OperationLogSerializer(serializers.ModelSerializer):
    """操作日志序列化器"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = OperationLog
        fields = [
            'id', 'action', 'action_display', 'module', 'object_type', 'object_id',
            'description', 'old_data', 'new_data', 'ip_address', 'request_path',
            'user_name', 'tenant_name', 'created_at'
        ]


class ScheduledTaskSerializer(serializers.ModelSerializer):
    """定时任务序列化器"""
    task_type_display = serializers.CharField(source='get_task_type_display', read_only=True)
    last_run_status_display = serializers.CharField(source='get_last_run_status_display', read_only=True)
    
    class Meta:
        model = ScheduledTask
        fields = '__all__'
        read_only_fields = ['tenant', 'last_run_at', 'last_run_status', 'last_run_result']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'content', 'notification_type', 'notification_type_display',
            'link_type', 'link_id', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['tenant', 'user']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NotificationReadSerializer(serializers.Serializer):
    """标记已读序列化器"""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
