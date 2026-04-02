from rest_framework import serializers
from .models import LogisticsCompany, ShippingMethod


class LogisticsCompanySerializer(serializers.ModelSerializer):
    """物流公司序列化器"""
    class Meta:
        model = LogisticsCompany
        fields = ['id', 'code', 'name', 'company_type', 'tracking_url']


class ShippingMethodSerializer(serializers.ModelSerializer):
    """物流渠道序列化器"""
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'code', 'method_type', 'company_name']
