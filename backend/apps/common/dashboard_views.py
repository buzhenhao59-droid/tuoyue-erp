from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

from apps.orders.models import Order
from apps.finance.models import Transaction
from apps.inventory.models import Inventory


class DashboardStatsView(APIView):
    """数据大屏统计"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tenant = request.tenant
        today = datetime.now().date()
        
        # 今日数据
        today_orders = Order.objects.filter(tenant=tenant, created_at__date=today)
        today_stats = {
            'total_orders': today_orders.count(),
            'valid_orders': today_orders.filter(status__in=['paid', 'shipped', 'completed']).count(),
            'total_amount': today_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        # 计算预估利润（简化计算：销售额 - 成本）
        today_profit = today_orders.filter(
            status__in=['paid', 'shipped', 'completed']
        ).aggregate(
            profit=Sum(F('total_amount') - F('product_amount') * 0.6)
        )['profit'] or 0
        
        today_stats['estimated_profit'] = round(today_profit, 2)
        today_stats['profit_rate'] = round(
            (today_profit / today_stats['total_amount'] * 100) if today_stats['total_amount'] > 0 else 0, 2
        )
        
        # 累计数据
        all_orders = Order.objects.filter(tenant=tenant)
        cumulative_stats = {
            'total_orders': all_orders.count(),
            'total_amount': all_orders.aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        # 平台分布
        platform_distribution = list(all_orders.values(
            'shop__platform__name'
        ).annotate(
            count=Count('id'),
            amount=Sum('total_amount')
        ))
        
        return Response({
            'code': 200,
            'data': {
                'today': today_stats,
                'cumulative': cumulative_stats,
                'platform_distribution': platform_distribution
            }
        })


class DashboardChartView(APIView):
    """数据大屏图表数据"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tenant = request.tenant
        days = int(request.query_params.get('days', 30))
        
        # 生成过去N天的日期列表
        dates = []
        sales_data = []
        profit_data = []
        
        for i in range(days - 1, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            dates.append(date.strftime('%m-%d'))
            
            # 当日订单
            day_orders = Order.objects.filter(
                tenant=tenant,
                created_at__date=date,
                status__in=['paid', 'shipped', 'completed']
            )
            
            # 销售额
            day_sales = day_orders.aggregate(total=Sum('total_amount'))['total'] or 0
            sales_data.append(round(float(day_sales), 2))
            
            # 利润（简化计算）
            day_profit = day_orders.aggregate(
                profit=Sum(F('total_amount') - F('product_amount') * 0.6)
            )['profit'] or 0
            profit_data.append(round(float(day_profit), 2))
        
        return Response({
            'code': 200,
            'data': {
                'dates': dates,
                'sales': sales_data,
                'profit': profit_data
            }
        })


class InventoryAlertView(APIView):
    """库存预警"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        tenant = request.tenant
        
        # 获取低库存商品
        low_stock_items = Inventory.objects.filter(
            tenant=tenant,
            quantity__lte=F('warning_threshold')
        ).select_related('sku', 'sku__product', 'warehouse')
        
        # 计算建议采购数量
        result = []
        for item in low_stock_items:
            # 模拟近7天销量
            recent_sales = item.sku.orderitem_set.filter(
                order__created_at__gte=datetime.now() - timedelta(days=7)
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            # 建议采购量 = 近7天销量 * 2 - 当前库存
            suggested_qty = max(recent_sales * 2 - item.quantity, 10)
            
            result.append({
                'sku_id': item.sku.id,
                'sku_code': item.sku.sku_code,
                'product_name': item.sku.product.name,
                'warehouse_name': item.warehouse.name,
                'current_stock': item.quantity,
                'warning_threshold': item.warning_threshold,
                'recent_7d_sales': recent_sales,
                'suggested_purchase_qty': suggested_qty
            })
        
        return Response({
            'code': 200,
            'data': result
        })
