"""
租户相关 Mixin
"""

from rest_framework import serializers


class TenantMixin:
    """租户 Mixin，自动获取当前用户的租户"""
    
    def get_tenant(self):
        """获取当前请求的租户"""
        return getattr(self.request.user, 'tenant', None)
    
    def get_serializer_context(self):
        """添加租户到序列化器上下文"""
        context = super().get_serializer_context()
        context['tenant'] = self.get_tenant()
        return context
    
    def perform_create(self, serializer):
        """创建时自动设置租户"""
        tenant = self.get_tenant()
        if tenant:
            serializer.save(tenant=tenant)
        else:
            serializer.save()
