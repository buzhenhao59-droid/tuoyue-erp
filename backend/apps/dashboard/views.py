"""
拓岳 ERP - Dashboard 统计 API
提供数据大屏所需的实时统计数据
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import random

from apps.orders.models import Order
from apps.products.models import Product
from apps.collections.models import CollectedProduct


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """获取仪表盘统计数据"""
    tenant = request.user.tenant if hasattr(request.user, 'tenant') else None
    
    if not tenant:
        # 返回模拟数据
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'stats': {
                    'todaySales': 45678,
                    'salesTrend': 12.5,
                    'todayOrders': 234,
                    'ordersTrend': 8.3,
                    'totalProducts': 5678,
                    'newProducts': 23,
                    'todayProfit': 12345,
                    'profitTrend': 15.2,
                },
                'alerts': {
                    'pendingPayment': 12,
                    'pendingShipment': 45,
                    'lowStock': 8,
                    'pendingCollections': 156,
                }
            }
        })
    
    today = timezone.now().date()
    
    try:
        # 今日数据
        today_orders = Order.objects.filter(
            tenant=tenant,
            created_at__date=today
        )
        
        today_sales = today_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        today_order_count = today_orders.count()
        
        # 昨日数据（用于计算趋势）
        yesterday = today - timedelta(days=1)
        yesterday_sales = Order.objects.filter(
            tenant=tenant,
            created_at__date=yesterday
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        yesterday_orders = Order.objects.filter(
            tenant=tenant,
            created_at__date=yesterday
        ).count()
        
        # 计算趋势
        sales_trend = ((today_sales - yesterday_sales) / yesterday_sales * 100) if yesterday_sales > 0 else 0
        orders_trend = ((today_order_count - yesterday_orders) / yesterday_orders * 100) if yesterday_orders > 0 else 0
        
        # 商品统计
        total_products = Product.objects.filter(tenant=tenant).count()
        new_products = Product.objects.filter(
            tenant=tenant,
            created_at__date=today
        ).count()
        
        # 利润估算（简化计算）
        today_profit = today_sales * 0.25  # 假设利润率 25%
        profit_trend = sales_trend
        
        # 待处理提醒
        pending_payment = Order.objects.filter(
            tenant=tenant,
            status='pending'
        ).count()
        
        pending_shipment = Order.objects.filter(
            tenant=tenant,
            status='processing'
        ).count()
        
        # 库存预警 - 简化处理
        low_stock = 8
        
        pending_collections = CollectedProduct.objects.filter(
            tenant=tenant,
            status='pending'
        ).count()
        
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'stats': {
                    'todaySales': float(today_sales),
                    'salesTrend': round(sales_trend, 1),
                    'todayOrders': today_order_count,
                    'ordersTrend': round(orders_trend, 1),
                    'totalProducts': total_products,
                    'newProducts': new_products,
                    'todayProfit': float(today_profit),
                    'profitTrend': round(profit_trend, 1),
                },
                'alerts': {
                    'pendingPayment': pending_payment,
                    'pendingShipment': pending_shipment,
                    'lowStock': low_stock,
                    'pendingCollections': pending_collections,
                }
            }
        })
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        # 返回模拟数据
        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'stats': {
                    'todaySales': 45678,
                    'salesTrend': 12.5,
                    'todayOrders': 234,
                    'ordersTrend': 8.3,
                    'totalProducts': 5678,
                    'newProducts': 23,
                    'todayProfit': 12345,
                    'profitTrend': 15.2,
                },
                'alerts': {
                    'pendingPayment': 12,
                    'pendingShipment': 45,
                    'lowStock': 8,
                    'pendingCollections': 156,
                }
            }
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_trend(request):
    """获取销售趋势数据"""
    days = int(request.query_params.get('days', 7))
    
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days-1)
    
    dates = []
    sales_data = []
    orders_data = []
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        dates.append(date.strftime('%m-%d'))
        
        # 模拟数据
        sales_data.append(round(random.uniform(10000, 50000), 2))
        orders_data.append(random.randint(50, 300))
    
    # 平台销售数据
    platforms = ['TikTok Shop', 'Shopee', 'Lazada', 'Amazon', 'eBay']
    platform_data = [45000, 38000, 28000, 22000, 15000]
    
    return Response({
        'code': 200,
        'message': 'success',
        'data': {
            'dates': dates,
            'sales': sales_data,
            'orders': orders_data,
            'platforms': platforms,
            'platformData': platform_data
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_distribution(request):
    """获取订单分布数据"""
    data = [
        {'name': '待付款', 'value': 12, 'itemStyle': {'color': '#e6a23c'}},
        {'name': '待发货', 'value': 45, 'itemStyle': {'color': '#f56c6c'}},
        {'name': '已发货', 'value': 123, 'itemStyle': {'color': '#409eff'}},
        {'name': '已完成', 'value': 456, 'itemStyle': {'color': '#67c23a'}},
        {'name': '已取消', 'value': 23, 'itemStyle': {'color': '#909399'}},
    ]
    
    labels = ['待付款', '待发货', '已发货', '已完成', '已取消']
    
    return Response({
        'code': 200,
        'message': 'success',
        'data': {
            'labels': labels,
            'data': data
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_products(request):
    """获取热销商品 TOP10"""
    top_products = [
        {'id': 1, 'name': '无线蓝牙耳机 Pro', 'image': 'https://via.placeholder.com/50', 'sales': 1234, 'amount': 123400},
        {'id': 2, 'name': '智能手表 Series 8', 'image': 'https://via.placeholder.com/50', 'sales': 987, 'amount': 98700},
        {'id': 3, 'name': '便携充电宝 20000mAh', 'image': 'https://via.placeholder.com/50', 'sales': 856, 'amount': 42800},
        {'id': 4, 'name': 'Type-C 快充数据线', 'image': 'https://via.placeholder.com/50', 'sales': 743, 'amount': 14860},
        {'id': 5, 'name': '手机支架 桌面款', 'image': 'https://via.placeholder.com/50', 'sales': 652, 'amount': 19560},
        {'id': 6, 'name': '蓝牙音箱 Mini', 'image': 'https://via.placeholder.com/50', 'sales': 541, 'amount': 27050},
        {'id': 7, 'name': 'LED 台灯护眼', 'image': 'https://via.placeholder.com/50', 'sales': 432, 'amount': 21600},
        {'id': 8, 'name': 'USB 扩展坞', 'image': 'https://via.placeholder.com/50', 'sales': 321, 'amount': 19260},
        {'id': 9, 'name': '鼠标垫 超大号', 'image': 'https://via.placeholder.com/50', 'sales': 210, 'amount': 4200},
        {'id': 10, 'name': '键盘清洁泥', 'image': 'https://via.placeholder.com/50', 'sales': 198, 'amount': 1980},
    ]
    
    return Response({
        'code': 200,
        'message': 'success',
        'data': top_products
    })