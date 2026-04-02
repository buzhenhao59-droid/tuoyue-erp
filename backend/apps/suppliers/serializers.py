from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderItem


class SupplierSerializer(serializers.ModelSerializer):
    """供应商序列化器"""
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'code', 'contact_person', 'contact_phone', 'contact_email', 'status']


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """采购订单明细序列化器"""
    sku_code = serializers.CharField(source='sku.sku_code', read_only=True)
    product_name = serializers.CharField(source='sku.product.name', read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['id', 'sku_code', 'product_name', 'quantity', 'received_quantity', 'unit_price', 'total_price']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """采购订单序列化器"""
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = ['id', 'po_no', 'supplier_name', 'warehouse_name', 'status', 
                  'total_amount', 'total_quantity', 'items', 'created_at']
