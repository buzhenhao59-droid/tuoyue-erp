from rest_framework import viewsets
from django_filters import rest_framework as filters

from apps.tenants.models import Tenant
from apps.tenants.serializers import TenantSerializer, TenantCreateSerializer


class TenantFilter(filters.FilterSet):
    """租户过滤器"""
    status = filters.BooleanFilter(field_name='status')
    plan = filters.CharFilter(field_name='plan')
    
    class Meta:
        model = Tenant
        fields = ['status', 'plan']


class TenantViewSet(viewsets.ModelViewSet):
    """租户管理视图集"""
    filterset_class = TenantFilter
    
    def get_queryset(self):
        # 普通用户只能看到自己的租户
        if not self.request.user.is_superuser:
            return Tenant.objects.filter(id=self.request.tenant.id)
        return Tenant.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
