"""
拓岳 ERP - 产品采集视图
支持多平台商品采集、批量操作、认领发布
"""

import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Count, Q
from django.utils import timezone

from .models import CollectionTask, CollectionConfig, CollectedProduct
from .serializers import (
    CollectionTaskSerializer, 
    CollectionTaskCreateSerializer, 
    CollectionConfigSerializer,
    CollectedProductSerializer,
    CollectedProductListSerializer
)
from .scraper import ScraperFactory


class CollectionConfigViewSet(viewsets.ModelViewSet):
    """采集配置视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = CollectionConfigSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_at', 'name']
    ordering = ['-is_default', '-created_at']
    
    def get_queryset(self):
        return CollectionConfig.objects.filter(tenant=self.request.tenant)
    
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
    """采集任务视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'source_platform', 'task_type']
    search_fields = ['name', 'task_no']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return CollectionTask.objects.filter(tenant=self.request.tenant)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionTaskCreateSerializer
        return CollectionTaskSerializer
    
    def create(self, request, *args, **kwargs):
        """创建采集任务"""
        urls_text = request.data.get('urls_text', '')
        config_id = request.data.get('config')
        task_type = request.data.get('task_type', 'link')
        auto_claim = request.data.get('auto_claim', False)
        
        # 解析链接
        urls = self._parse_urls(urls_text)
        if not urls:
            return Response({
                'code': 400,
                'message': '未检测到有效链接',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取配置
        config = None
        if config_id:
            try:
                config = CollectionConfig.objects.get(
                    id=config_id, 
                    tenant=request.tenant
                )
            except CollectionConfig.DoesNotExist:
                pass
        
        # 如果没有指定配置，使用默认配置
        if not config:
            config = CollectionConfig.objects.filter(
                tenant=request.tenant,
                is_default=True
            ).first()
        
        # 创建任务
        task = CollectionTask.objects.create(
            tenant=request.tenant,
            user=request.user,
            config=config,
            task_type=task_type,
            source_urls=[{'url': url, 'platform': self._detect_platform(url), 'status': 'pending'} for url in urls],
            source_platform=self._detect_platform(urls[0]) if urls else '',
            total_count=len(urls),
            status='pending'
        )
        
        # 异步执行采集（实际项目中应使用 Celery）
        # execute_collection_task.delay(task.id)
        
        return Response({
            'code': 200,
            'message': f'成功创建采集任务，共 {len(urls)} 个链接',
            'data': CollectionTaskSerializer(task).data
        })
    
    def _parse_urls(self, text: str) -> list:
        """解析链接文本"""
        # 支持换行或 $$ 分隔
        import re
        urls = re.split(r'[\n\r]+|\$\$', text)
        return [url.strip() for url in urls if url.strip().startswith('http')]
    
    def _detect_platform(self, url: str) -> str:
        """检测平台"""
        url_lower = url.lower()
        if '1688.com' in url_lower:
            return '1688'
        elif 'taobao.com' in url_lower:
            return 'taobao'
        elif 'tmall.com' in url_lower:
            return 'tmall'
        elif 'shopee' in url_lower:
            return 'shopee'
        elif 'lazada' in url_lower:
            return 'lazada'
        elif 'tiktok' in url_lower:
            return 'tiktok'
        return 'unknown'
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行采集任务"""
        task = self.get_object()
        task.status = 'processing'
        task.started_at = timezone.now()
        task.save()
        
        success_count = 0
        fail_count = 0
        
        for item in task.source_urls:
            url = item.get('url')
            platform = item.get('platform')
            
            try:
                # 获取对应平台的爬虫
                scraper = ScraperFactory.get_scraper(platform)
                if not scraper:
                    item['status'] = 'failed'
                    item['error'] = f'不支持的平台: {platform}'
                    fail_count += 1
                    continue
                
                # 执行采集
                product_data = scraper.scrape(url)
                if not product_data:
                    item['status'] = 'failed'
                    item['error'] = '采集失败，无法获取商品数据'
                    fail_count += 1
                    continue
                
                # 创建采集商品记录
                self._create_collected_product(task, product_data)
                
                item['status'] = 'success'
                success_count += 1
                
            except Exception as e:
                item['status'] = 'failed'
                item['error'] = str(e)
                fail_count += 1
        
        # 更新任务状态
        task.source_urls = task.source_urls
        task.status = 'completed' if fail_count == 0 else 'partial'
        task.success_count = success_count
        task.fail_count = fail_count
        task.completed_at = timezone.now()
        task.save()
        
        return Response({
            'code': 200,
            'message': '采集完成',
            'data': {
                'success': success_count,
                'failed': fail_count
            }
        })
    
    def _create_collected_product(self, task: CollectionTask, data: dict):
        """创建采集商品记录"""
        config = task.config
        
        # 价格转换
        original_price = data.get('price', 0)
        if config:
            price_multiplier = float(config.price_multiplier)
            price_addition = float(config.price_addition)
            converted_price = original_price * price_multiplier + price_addition
            
            # 价格区间保护
            if config.min_price and converted_price < float(config.min_price):
                converted_price = float(config.min_price)
            if config.max_price and converted_price > float(config.max_price):
                converted_price = float(config.max_price)
        else:
            converted_price = original_price
        
        # 创建商品记录
        product = CollectedProduct.objects.create(
            tenant=task.tenant,
            task=task,
            config=config,
            source_url=data.get('source_url', ''),
            source_platform=data.get('source_platform', ''),
            source_id=data.get('source_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            main_image=data.get('main_image', ''),
            images=data.get('images', []),
            original_price_min=original_price,
            original_price_max=original_price,
            price_min=converted_price,
            price_max=converted_price,
            currency=data.get('currency', 'CNY'),
            sku_attributes=data.get('sku_attributes', []),
            skus=data.get('skus', []),
            sku_count=len(data.get('skus', [])),
            source_category_name=data.get('category_name', ''),
            brand=data.get('brand', ''),
            weight=data.get('weight'),
            raw_data=data.get('raw_data', {}),
            status='pending'
        )
        
        return product


class CollectedProductViewSet(viewsets.ModelViewSet):
    """采集商品视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'source_platform']
    search_fields = ['title', 'source_id']
    ordering_fields = ['created_at', 'price_min', 'original_price_min']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return CollectedProduct.objects.filter(tenant=self.request.tenant)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CollectedProductListSerializer
        return CollectedProductSerializer
    
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
        response.data['stats'] = stats
        
        return response
    
    def _get_stats(self, request):
        """获取统计信息"""
        queryset = self.get_queryset()
        
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
        }
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """认领商品"""
        product = self.get_object()
        
        if product.status != 'pending':
            return Response({
                'code': 400,
                'message': '该商品已被处理',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product.status = 'claimed'
        product.claimed_by = request.user
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
        
        product.status = 'ignored'
        product.save()
        
        return Response({
            'code': 200,
            'message': '已忽略',
            'data': self.get_serializer(product).data
        })
    
    @action(detail=False, methods=['post'])
    def batch_claim(self, request):
        """批量认领"""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({
                'code': 400,
                'message': '请选择要认领的商品',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        count = self.get_queryset().filter(
            id__in=ids,
            status='pending'
        ).update(
            status='claimed',
            claimed_by=request.user,
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
            return Response({
                'code': 400,
                'message': '请选择要忽略的商品',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        count = self.get_queryset().filter(id__in=ids).update(status='ignored')
        
        return Response({
            'code': 200,
            'message': f'成功忽略 {count} 个商品',
            'data': {'count': count}
        })
    
    @action(detail=False, methods=['post'])
    def batch_update_price(self, request):
        """批量改价"""
        ids = request.data.get('ids', [])
        price_type = request.data.get('price_type', 'multiply')
        value = float(request.data.get('value', 1.5))
        value2 = request.data.get('value2')
        
        if not ids:
            return Response({
                'code': 400,
                'message': '请选择要改价的商品',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        products = self.get_queryset().filter(id__in=ids)
        updated_count = 0
        
        for product in products:
            original_price = float(product.original_price_min or 0)
            
            if price_type == 'multiply':
                new_price = original_price * value
            elif price_type == 'add':
                new_price = original_price + value
            elif price_type == 'fixed':
                new_price = value
            elif price_type == 'range' and value2:
                import random
                new_price = random.uniform(value, float(value2))
            else:
                continue
            
            product.price_min = round(new_price, 2)
            product.price_max = round(new_price, 2)
            product.save()
            updated_count += 1
        
        return Response({
            'code': 200,
            'message': f'成功修改 {updated_count} 个商品价格',
            'data': {'count': updated_count}
        })
    
    @action(detail=False, methods=['post'])
    def batch_push(self, request):
        """批量推送到店铺"""
        ids = request.data.get('ids', [])
        shop_ids = request.data.get('shop_ids', [])
        
        if not ids or not shop_ids:
            return Response({
                'code': 400,
                'message': '请选择商品和目标店铺',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 这里实现推送到店铺的逻辑
        # 实际项目中应调用各平台的API
        
        count = self.get_queryset().filter(id__in=ids).update(
            status='published',
            published_shops=[{'shop_id': sid, 'status': 'pending'} for sid in shop_ids]
        )
        
        return Response({
            'code': 200,
            'message': f'成功推送 {count} 个商品到 {len(shop_ids)} 个店铺',
            'data': {'count': count}
        })