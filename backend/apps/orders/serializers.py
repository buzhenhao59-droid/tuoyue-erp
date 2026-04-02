from rest_framework import serializers
from .models import Order, OrderItem, OrderShipment


class OrderItemSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'sku_name', 'image', 'quantity', 
                  'unit_price', 'total_price', 'cost_price']


class OrderShipmentSerializer(serializers.ModelSerializer):
    """订单物流序列化器"""
    class Meta:
        model = OrderShipment
        fields = ['id', 'tracking_no', 'carrier_name', 'carrier_code', 
                  'shipping_method', 'status', 'shipped_at', 'delivered_at']


class OrderSerializer(serializers.ModelSerializer):
    """订单序列化器"""
    items = OrderItemSerializer(many=True, read_only=True)
    shipments = OrderShipmentSerializer(many=True, read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    platform_name = serializers.CharField(source='shop.platform.name', read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'platform_order_no', 'shop_name', 'platform_name',
                  'status', 'currency', 'total_amount', 'product_amount', 'shipping_fee',
                  'discount_amount', 'paid_amount', 'buyer_name', 'receiver_name',
                  'receiver_country', 'receiver_address', 'paid_at', 'shipped_at',
                  'items', 'shipments', 'created_at']


class OrderListSerializer(serializers.ModelSerializer):
    """订单列表序列化器（简化）"""
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    platform_name = serializers.CharField(source='shop.platform.name', read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ['id', 'order_no', 'platform_order_no', 'shop_name', 'platform_name',
                  'status', 'total_amount', 'currency', 'buyer_name', 'receiver_country',
                  'item_count', 'created_at']
    
    def get_item_count(self, obj):
        return obj.items.count()
