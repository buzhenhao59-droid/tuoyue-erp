"""
采集模块 API 视图（妙手 ERP 深度克隆版）
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
import json

from apps.common.pagination import StandardResultsSetPagination
from .models import CollectionConfig, CollectionTask, CollectedProduct, CollectionPluginLog
from .serializers import (
    CollectionConfigSerializer,
    CollectionConfigSimpleSerializer,
    CollectionTaskSerializer,
    CollectionTaskCreateSerializer,
    CollectedProductListSerializer,
    CollectedProductDetailSerializer,
    CollectedProductUpdateSerializer,
    BatchUpdatePriceSerializer,
    BatchPushToShopSerializer,
    PluginWebhookSerializer,
    CollectionStatsSerializer
)
from .scraper import ScraperFactory


class CollectionConfigViewSet(viewsets.ModelViewSet):
    """采集配置管理"""
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        return CollectionConfig.objects.filter(tenant=tenant).order_by('-is_default', '-created_at')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CollectionConfigSimpleSerializer
        return CollectionConfigSerializer
    
    def perform_create(self, serializer):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        serializer.save(tenant=tenant)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """设为默认配置"""
        config = self.get_object()
        
        # 取消其他默认配置
        self.get_queryset().filter(is_default=True).update(is_default=False)
        
        config.is_default = True
        config.save()
        
        return Response({
            'code': 200,
            'message': '已设为默认配置',
            'data': self.get_serializer(config).data
        })


class CollectionTaskViewSet(viewsets.ModelViewSet):
    """采集任务管理"""
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionTaskCreateSerializer
        return CollectionTaskSerializer
    
    def get_queryset(self):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        return CollectionTask.objects.filter(tenant=tenant).order_by('-created_at')
    
    def perform_create(self, serializer):
        from apps.tenants.models import Tenant
        from apps.users.models import User
        
        tenant = Tenant.objects.first()
        user = User.objects.first()
        
        task = serializer.save(tenant=tenant, user=user)
        
        # 启动采集任务（异步）
        from .tasks import process_collection_task
        process_collection_task.delay(task.id)
        
        return task
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重试任务"""
        task = self.get_object()
        if task.status not in ['failed', 'partial']:
            return Response({'error': '只能重试失败或部分成功的任务'}, status=400)
        
        task.status = 'pending'
        task.retry_count += 1
        task.error_msg = ''
        task.save()
        
        from .tasks import process_collection_task
        process_collection_task.delay(task.id)
        
        return Response({'message': '任务已重新启动'})


class CollectedProductViewSet(viewsets.ModelViewSet):
    """采集商品管理"""
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CollectedProductDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return CollectedProductUpdateSerializer
        return CollectedProductListSerializer
    
    def get_queryset(self):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        
        queryset = CollectedProduct.objects.filter(tenant=tenant)
        
        # 平台筛选
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(source_platform=platform)
        
        # 状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 日期筛选
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        
        # 关键词搜索
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | 
                Q(source_id__icontains=keyword) |
                Q(source_url__icontains=keyword)
            )
        
        return queryset.select_related('claimed_by', 'editor').order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """列表查询，包含统计信息"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
        
        # 添加统计数据
        stats = self._get_stats(request)
        if isinstance(response.data, dict):
            response.data['stats'] = stats
        
        return response
    
    def _get_stats(self, request):
        """获取统计信息"""
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        queryset = CollectedProduct.objects.filter(tenant=tenant)
        
        # 应用过滤条件（除了status）
        platform = request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(source_platform=platform)
        
        return {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'claimed': queryset.filter(status='claimed').count(),
            'editing': queryset.filter(status='editing').count(),
            'published': queryset.filter(status='published').count(),
            'ignored': queryset.filter(status='ignored').count(),
            'failed': queryset.filter(status='failed').count(),
        }
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """认领商品"""
        product = self.get_object()
        if product.status != 'pending':
            return Response({'error': '该商品已被处理'}, status=400)
        
        from apps.users.models import User
        user = User.objects.first()
        
        product.status = 'claimed'
        product.claimed_by = user
        product.claimed_at = timezone.now()
        product.save()
        
        return Response({
            'code': 200,
            'message': '认领成功',
            'data': self.get_serializer(product).data
        })
    
    @action(detail=True, methods=['post'])
    def ignore(self, request, pk=None):
        """忽略商品"""
        product = self.get_object()
        if product.status not in ['pending', 'claimed']:
            return Response({'error': '该商品状态不允许忽略'}, status=400)
        
        product.status = 'ignored'
        product.save()
        
        return Response({
            'code': 200,
            'message': '已忽略',
            'data': self.get_serializer(product).data
        })
    
    @action(detail=True, methods=['post'])
    def start_edit(self, request, pk=None):
        """开始编辑"""
        product = self.get_object()
        if product.status not in ['pending', 'claimed']:
            return Response({'error': '该商品状态不允许编辑'}, status=400)
        
        from apps.users.models import User
        user = User.objects.first()
        
        product.status = 'editing'
        product.editor = user
        product.editing_at = timezone.now()
        product.save()
        
        return Response({'message': '开始编辑'})
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布商品"""
        product = self.get_object()
        shop_ids = request.data.get('shop_ids', [])
        
        if not shop_ids:
            return Response({'error': '请选择目标店铺'}, status=400)
        
        # TODO: 调用平台API发布商品
        # 这里模拟发布成功
        
        product.status = 'published'
        product.published_shops = [
            {'shop_id': sid, 'platform': 'shopee', 'status': 'success', 'time': timezone.now().isoformat()}
            for sid in shop_ids
        ]
        product.save()
        
        return Response({
            'code': 200,
            'message': '发布成功',
            'data': {
                'published_shops': product.published_shops
            }
        })
    
    @action(detail=False, methods=['post'])
    def batch_claim(self, request):
        """批量认领"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择商品'}, status=400)
        
        from apps.users.models import User
        from apps.tenants.models import Tenant
        
        tenant = Tenant.objects.first()
        user = User.objects.filter(tenant=tenant).first()
        
        count = CollectedProduct.objects.filter(
            tenant=tenant,
            id__in=ids,
            status='pending'
        ).update(
            status='claimed',
            claimed_by=user,
            claimed_at=timezone.now()
        )
        
        return Response({
            'code': 200,
            'message': f'成功认领 {count} 个商品',
            'data': {'count': count}
        })
    
    @action(detail=False, methods=['post'])
    def batch_ignore(self, request):
        """批量忽略"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '请选择商品'}, status=400)
        
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        
        count = CollectedProduct.objects.filter(
            tenant=tenant,
            id__in=ids,
            status__in=['pending', 'claimed']
        ).update(status='ignored')
        
        return Response({
            'code': 200,
            'message': f'成功忽略 {count} 个商品',
            'data': {'count': count}
        })
    
    @action(detail=False, methods=['post'])
    def batch_update_price(self, request):
        """批量修改价格"""
        serializer = BatchUpdatePriceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ids = serializer.validated_data['ids']
        price_type = serializer.validated_data['price_type']
        value = serializer.validated_data['value']
        
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        
        products = CollectedProduct.objects.filter(tenant=tenant, id__in=ids)
        
        for product in products:
            if price_type == 'fixed':
                product.price_min = value
                product.price_max = value
            elif price_type == 'multiplier':
                if product.original_price_min:
                    product.price_min = product.original_price_min * value
                if product.original_price_max:
                    product.price_max = product.original_price_max * value
            elif price_type == 'addition':
                if product.original_price_min:
                    product.price_min = product.original_price_min + value
                if product.original_price_max:
                    product.price_max = product.original_price_max + value
            product.save()
        
        return Response({
            'code': 200,
            'message': f'成功更新 {len(ids)} 个商品价格',
            'data': {'count': len(ids)}
        })
    
    @action(detail=False, methods=['post'])
    def batch_push(self, request):
        """批量推送到店铺"""
        serializer = BatchPushToShopSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ids = serializer.validated_data['ids']
        shop_ids = serializer.validated_data['shop_ids']
        
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        
        products = CollectedProduct.objects.filter(tenant=tenant, id__in=ids)
        
        for product in products:
            product.status = 'published'
            product.published_shops = [
                {'shop_id': sid, 'platform': 'shopee', 'status': 'success', 'time': timezone.now().isoformat()}
                for sid in shop_ids
            ]
            product.save()
        
        return Response({
            'code': 200,
            'message': f'成功推送 {len(ids)} 个商品到 {len(shop_ids)} 个店铺',
            'data': {'count': len(ids)}
        })


class CollectionStatsViewSet(viewsets.ViewSet):
    """采集统计"""
    permission_classes = [AllowAny]
    
    def list(self, request):
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        
        stats = CollectedProduct.objects.filter(tenant=tenant).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            claimed=Count('id', filter=Q(status='claimed')),
            editing=Count('id', filter=Q(status='editing')),
            published=Count('id', filter=Q(status='published')),
            ignored=Count('id', filter=Q(status='ignored')),
            failed=Count('id', filter=Q(status='failed'))
        )
        
        # 按平台统计
        platform_stats = CollectedProduct.objects.filter(tenant=tenant).values('source_platform').annotate(
            count=Count('id')
        )
        
        by_platform = {item['source_platform']: item['count'] for item in platform_stats}
        
        data = {
            **stats,
            'by_platform': by_platform
        }
        
        return Response(data)


class PluginWebhookViewSet(viewsets.ViewSet):
    """插件 Webhook 接收"""
    permission_classes = [AllowAny]
    
    def create(self, request):
        """接收插件推送的数据"""
        serializer = PluginWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.tenants.models import Tenant
        tenant = Tenant.objects.first()
        
        # 创建插件日志
        log = CollectionPluginLog.objects.create(
            tenant=tenant,
            plugin_id=serializer.validated_data['plugin_id'],
            plugin_version=serializer.validated_data['plugin_version'],
            payload=serializer.validated_data['data'],
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # 异步处理插件数据
        from .tasks import process_plugin_data
        process_plugin_data.delay(log.id)
        
        return Response({
            'code': 200,
            'message': '数据已接收',
            'data': {'log_id': log.id}
        })


class BatchImportViewSet(viewsets.ViewSet):
    """批量导入"""
    permission_classes = [AllowAny]
    
    def create(self, request):
        """批量导入商品链接"""
        file = request.FILES.get('file')
        platform = request.data.get('platform', '1688')
        config_id = request.data.get('config_id')
        
        if not file:
            return Response({'error': '请上传文件'}, status=400)
        
        # 解析文件
        import pandas as pd
        from io import BytesIO
        
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(BytesIO(file.read()))
            else:
                df = pd.read_excel(BytesIO(file.read()))
        except Exception as e:
            return Response({'error': f'文件解析失败: {str(e)}'}, status=400)
        
        # 处理数据
        success_count = 0
        fail_count = 0
        errors = []
        
        urls = []
        for idx, row in df.iterrows():
            try:
                url = row.get('商品链接') or row.get('url') or row.get('链接')
                if url and str(url).startswith('http'):
                    urls.append(str(url))
                    success_count += 1
                else:
                    fail_count += 1
                    errors.append({'row': idx + 2, 'url': url, 'error': '无效的链接'})
            except Exception as e:
                fail_count += 1
                errors.append({'row': idx + 2, 'url': '', 'error': str(e)})
        
        # 创建采集任务
        if urls:
            from apps.tenants.models import Tenant
            from apps.users.models import User
            
            tenant = Tenant.objects.first()
            user = User.objects.first()
            
            config = None
            if config_id:
                config = CollectionConfig.objects.filter(id=config_id, tenant=tenant).first()
            
            task = CollectionTask.objects.create(
                tenant=tenant,
                user=user,
                config=config,
                task_type='import',
                source_urls=[{'url': url, 'platform': platform, 'status': 'pending'} for url in urls],
                source_platform=platform,
                total_count=len(urls),
                status='pending'
            )
            
            # 启动采集任务
            from .tasks import process_collection_task
            process_collection_task.delay(task.id)
        
        return Response({
            'code': 200,
            'message': '导入成功',
            'data': {
                'success_count': success_count,
                'fail_count': fail_count,
                'errors': errors[:10],  # 最多返回10条错误
                'task_id': task.id if urls else None
            }
        })


class AISelectionViewSet(viewsets.ViewSet):
    """AI选品"""
    permission_classes = [AllowAny]
    
    def list(self, request):
        """AI智能选品分析"""
        platform = request.query_params.get('platform')
        category = request.query_params.get('category')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        keyword = request.query_params.get('keyword')
        limit = int(request.query_params.get('limit', 20))
        
        # 模拟AI分析结果
        analysis = {
            'market_trend': 'up',
            'competition_level': 'medium',
            'profit_potential': 'high',
            'recommendation_score': 85
        }
        
        # 模拟推荐商品
        products = []
        for i in range(min(limit, 10)):
            products.append({
                'id': i + 1,
                'title': f'推荐商品 {i + 1} - {keyword or "热门商品"}',
                'main_image': f'https://via.placeholder.com/300x300?text=Product+{i+1}',
                'score': 90 - i * 5,
                'estimated_price': 100 + i * 10,
                'estimated_profit': 30 + i * 5,
                'sales_volume': f'{1000 + i * 500}+',
                'competition_count': 50 + i * 10,
            })
        
        return Response({
            'code': 200,
            'data': {
                'analysis': analysis,
                'products': products
            }
        })
