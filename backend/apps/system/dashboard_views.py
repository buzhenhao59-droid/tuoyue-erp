from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import datetime, timedelta

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.inventory.models import Inventory
from apps.finance.models import Transaction, PlatformBill


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """数据大屏概览"""
    tenant = request.tenant
    today = timezone.now().date()
    
    # 今日数据
    today_start = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    today_orders = Order.objects.filter(tenant=tenant, created_at__gte=today_start)
    
    today_stats = {
        'order_count': today_orders.count(),
        'order_amount': today_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        'paid_order_count': today_orders.filter(status__gte=1).count(),
    }
    
    # 本月数据
    month_start = today.replace(day=1)
    month_orders = Order.objects.filter(tenant=tenant, created_at__date__gte=month_start)
    
    month_stats = {
        'order_count': month_orders.count(),
        'order_amount': month_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
    }
    
    # 总数据
    total_stats = {
        'product_count': Product.objects.filter(tenant=tenant).count(),
        'sku_count': Inventory.objects.filter(tenant=tenant).count(),
        'low_stock_count': Inventory.objects.filter(tenant=tenant, quantity__lte=F('warning_threshold')).count(),
    }
    
    # 待处理事项
    pending_stats = {
        'pending_shipment': Order.objects.filter(tenant=tenant, status=1).count(),  # 待发货
        'pending_payment': Order.objects.filter(tenant=tenant, status=0).count(),  # 待付款
        'low_stock': total_stats['low_stock_count'],
    }
    
    return Response({
        'today': today_stats,
        'month': month_stats,
        'total': total_stats,
        'pending': pending_stats
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_trend(request):
    """销售趋势（近30天）"""
    tenant = request.tenant
    days = int(request.query_params.get('days', 30))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    # 生成日期列表
    date_list = []
    current = start_date
    while current <= end_date:
        date_list.append(current)
        current += timedelta(days=1)
    
    # 查询每日数据
    daily_data = Order.objects.filter(
        tenant=tenant,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('created_at__date').annotate(
        order_count=Count('id'),
        order_amount=Sum('total_amount'),
        product_quantity=Sum('items__quantity')
    ).order_by('created_at__date')
    
    # 构建结果
    data_dict = {d['created_at__date']: d for d in daily_data}
    
    result = []
    for date in date_list:
        data = data_dict.get(date, {
            'order_count': 0,
            'order_amount': 0,
            'product_quantity': 0
        })
        result.append({
            'date': date.strftime('%Y-%m-%d'),
            'order_count': data.get('order_count', 0),
            'order_amount': float(data.get('order_amount', 0) or 0),
            'product_quantity': data.get('product_quantity', 0) or 0
        })
    
    return Response({
        'days': days,
        'data': result
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_by_country(request):
    """按国家销售统计"""
    tenant = request.tenant
    days = int(request.query_params.get('days', 30))
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    country_data = Order.objects.filter(
        tenant=tenant,
        created_at__date__gte=start_date
    ).values('receiver_country').annotate(
        order_count=Count('id'),
        order_amount=Sum('total_amount')
    ).order_by('-order_amount')[:10]
    
    return Response({
        'data': list(country_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_by_platform(request):
    """按平台销售统计"""
    tenant = request.tenant
    days = int(request.query_params.get('days', 30))
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    platform_data = Order.objects.filter(
        tenant=tenant,
        created_at__date__gte=start_date
    ).values('shop__platform__name').annotate(
        order_count=Count('id'),
        order_amount=Sum('total_amount')
    ).order_by('-order_amount')
    
    return Response({
        'data': list(platform_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_products(request):
    """热销商品排行"""
    tenant = request.tenant
    days = int(request.query_params.get('days', 30))
    limit = int(request.query_params.get('limit', 10))
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    top_products = OrderItem.objects.filter(
        tenant=tenant,
        order__created_at__date__gte=start_date
    ).values(
        'product__id', 'product__name', 'sku__sku_code'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_amount=Sum('total_price'),
        order_count=Count('order', distinct=True)
    ).order_by('-total_quantity')[:limit]
    
    return Response({
        'data': list(top_products)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_status_distribution(request):
    """订单状态分布"""
    tenant = request.tenant
    days = int(request.query_params.get('days', 30))
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    status_data = Order.objects.filter(
        tenant=tenant,
        created_at__date__gte=start_date
    ).values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    status_map = dict(Order.ORDER_STATUS_CHOICES)
    
    result = []
    for item in status_data:
        result.append({
            'status': item['status'],
            'status_name': status_map.get(item['status'], '未知'),
            'count': item['count']
        })
    
    return Response({
        'data': result
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_distribution(request):
    """库存分布统计"""
    tenant = request.tenant
    
    # 按仓库分布
    warehouse_data = Inventory.objects.filter(
        tenant=tenant
    ).values('warehouse__name').annotate(
        sku_count=Count('id'),
        total_quantity=Sum('quantity')
    )
    
    # 库存状态分布
    total_count = Inventory.objects.filter(tenant=tenant).count()
    low_stock_count = Inventory.objects.filter(
        tenant=tenant,
        quantity__lte=F('warning_threshold')
    ).count()
    zero_stock_count = Inventory.objects.filter(
        tenant=tenant,
        quantity=0
    ).count()
    normal_count = total_count - low_stock_count
    
    return Response({
        'warehouse_distribution': list(warehouse_data),
        'stock_status': {
            'normal': normal_count,
            'low_stock': low_stock_count - zero_stock_count,
            'zero_stock': zero_stock_count
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_overview(request):
    """财务概览"""
    tenant = request.tenant
    days = int(request.query_params.get('days', 30))
    
    start_date = timezone.now().date() - timedelta(days=days)
    
    # 收入支出统计
    transaction_data = Transaction.objects.filter(
        tenant=tenant,
        transaction_date__gte=start_date
    ).values('transaction_type').annotate(
        total_amount=Sum('amount')
    )
    
    income = 0
    expense = 0
    for item in transaction_data:
        if item['transaction_type'] == 'income':
            income = item['total_amount'] or 0
        elif item['transaction_type'] == 'expense':
            expense = item['total_amount'] or 0
    
    # 分类统计
    category_data = Transaction.objects.filter(
        tenant=tenant,
        transaction_date__gte=start_date
    ).values('category').annotate(
        total_amount=Sum('amount')
    ).order_by('-total_amount')
    
    return Response({
        'income': income,
        'expense': expense,
        'profit': income - expense,
        'category_breakdown': list(category_data)
    })
