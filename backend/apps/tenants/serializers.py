from rest_framework import serializers
from apps.tenants.models import Tenant


class TenantSerializer(serializers.ModelSerializer):
    """租户序列化器"""
    
    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'code', 'status', 'plan', 'expired_at',
            'contact_name', 'contact_phone', 'contact_email',
            'settings', 'created_at', 'updated_at'
        ]


class TenantCreateSerializer(serializers.ModelSerializer):
    """租户创建序列化器"""
    
    class Meta:
        model = Tenant
        fields = ['name', 'code', 'contact_name', 'contact_phone', 'contact_email']
