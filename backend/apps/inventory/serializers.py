from rest_framework import serializers
from .models import Warehouse, Inventory


class WarehouseSerializer(serializers.ModelSerializer):
    """仓库序列化器"""
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'code', 'type', 'country', 'city', 'address', 'is_default', 'status']


class InventorySerializer(serializers.ModelSerializer):
    """库存序列化器"""
    product_name = serializers.CharField(source='sku.product.name', read_only=True)
    sku_code = serializers.CharField(source='sku.sku_code', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'product_name', 'sku_code', 'warehouse_name', 'quantity', 
                  'locked_quantity', 'warning_threshold', 'status']
