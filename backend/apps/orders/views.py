from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Count, Q, F
from datetime import datetime, timedelta

from .models import Order, OrderItem, OrderShipment
from .serializers import OrderSerializer, OrderListSerializer, OrderShipmentSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """订单视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'shop', 'platform_id']
    search_fields = ['order_no', 'platform_order_no', 'buyer_name', 'receiver_name']
    ordering_fields = ['created_at', 'paid_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Order.objects.filter(tenant=self.request.tenant)
        
        # 高级筛选
        params = self.request.query_params
        
        # 日期范围
        date_from = params.get('date_from')
        date_to = params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # 金额范围
        amount_min = params.get('amount_min')
        amount_max = params.get('amount_max')
        if amount_min:
            queryset = queryset.filter(total_amount__gte=amount_min)
        if amount_max:
            queryset = queryset.filter(total_amount__lte=amount_max)
        
        # 国家筛选
        country = params.get('country')
        if country:
            queryset = queryset.filter(receiver_country__icontains=country)
        
        return queryset.select_related('shop', 'shop__platform').prefetch_related('items', 'shipments')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderSerializer
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """订单统计"""
        queryset = self.get_queryset()
        
        stats = {
            'total_orders': queryset.count(),
            'total_amount': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'pending_count': queryset.filter(status='pending').count(),
            'paid_count': queryset.filter(status='paid').count(),
            'shipped_count': queryset.filter(status='shipped').count(),
            'completed_count': queryset.filter(status='completed').count(),
        }
        
        return Response({'code': 200, 'data': stats})
    
    @action(detail=True, methods=['post'])
    def apply_tracking(self, request, pk=None):
        """申请运单号（Mock）"""
        order = self.get_object()
        
        carrier_id = request.data.get('carrier_id')
        shipping_method = request.data.get('shipping_method', 'standard')
        
        # Mock生成运单号
        import random
        tracking_no = f'TRK{datetime.now().strftime("%Y%m%d")}{random.randint(100000, 999999)}'
        
        # 创建物流记录
        shipment = OrderShipment.objects.create(
            tenant=request.tenant,
            order=order,
            tracking_no=tracking_no,
            carrier_id=carrier_id or 1,
            carrier_name=request.data.get('carrier_name', 'Mock物流'),
            carrier_code=request.data.get('carrier_code', 'mock'),
            shipping_method=shipping_method,
            status='pending'
        )
        
        # 更新订单状态
        order.status = 'shipped'
        order.shipped_at = datetime.now()
        order.save()
        
        return Response({
            'code': 200,
            'message': '运单号申请成功',
            'data': {
                'tracking_no': tracking_no,
                'shipment': OrderShipmentSerializer(shipment).data
            }
        })
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """更新订单状态"""
        order = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return Response({
                'code': 400,
                'message': f'无效的状态: {new_status}'
            }, status=400)
        
        order.status = new_status
        
        if new_status == 'paid':
            order.paid_at = datetime.now()
        elif new_status == 'shipped':
            order.shipped_at = datetime.now()
        elif new_status == 'completed':
            order.completed_at = datetime.now()
        
        order.save()
        
        return Response({
            'code': 200,
            'message': '状态更新成功',
            'data': OrderSerializer(order).data
        })
    
    @action(detail=False, methods=['post'])
    def batch_process(self, request):
        """批量处理订单"""
        order_ids = request.data.get('order_ids', [])
        action_type = request.data.get('action')
        
        orders = Order.objects.filter(id__in=order_ids, tenant=request.tenant)
        
        if action_type == 'ship':
            # 批量发货
            count = 0
            for order in orders:
                if order.status == 'paid':
                    order.status = 'shipped'
                    order.shipped_at = datetime.now()
                    order.save()
                    count += 1
            return Response({
                'code': 200,
                'message': f'成功发货 {count} 个订单'
            })
        
        return Response({
            'code': 400,
            'message': '未知的操作类型'
        }, status=400)
