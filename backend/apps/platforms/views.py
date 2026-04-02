from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from apps.platforms.models import Platform, Shop
from apps.platforms.serializers import (
    PlatformSerializer, ShopListSerializer, ShopDetailSerializer,
    ShopCreateSerializer, ShopAuthSerializer, OAuthUrlSerializer, ShopSyncSerializer
)


class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    """电商平台视图集"""
    serializer_class = PlatformSerializer
    queryset = Platform.objects.filter(status=True)


class ShopFilter(filters.FilterSet):
    """店铺过滤器"""
    platform = filters.NumberFilter(field_name='platform_id')
    status = filters.NumberFilter(field_name='status')
    
    class Meta:
        model = Shop
        fields = ['platform', 'status']


class ShopViewSet(viewsets.ModelViewSet):
    """店铺管理视图集"""
    filterset_class = ShopFilter
    
    def get_queryset(self):
        return Shop.objects.filter(
            tenant=self.request.tenant
        ).select_related('platform')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ShopListSerializer
        elif self.action == 'create':
            return ShopCreateSerializer
        return ShopDetailSerializer
    
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """店铺授权（OAuth模拟）"""
        shop = self.get_object()
        serializer = ShopAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        auth_code = serializer.validated_data['auth_code']
        
        # Mock OAuth授权流程
        # 实际项目中这里会调用平台的OAuth接口
        
        # 模拟授权成功
        shop.auth_token = f"mock_access_token_{uuid.uuid4().hex[:16]}"
        shop.refresh_token = f"mock_refresh_token_{uuid.uuid4().hex[:16]}"
        shop.token_expires_at = timezone.now() + timedelta(days=30)
        shop.status = 1  # 启用
        shop.save()
        
        return Response({
            'message': '授权成功',
            'shop': ShopDetailSerializer(shop).data
        })
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """刷新授权令牌"""
        shop = self.get_object()
        
        if not shop.refresh_token:
            return Response(
                {'error': '店铺未授权'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mock刷新令牌
        shop.auth_token = f"mock_access_token_{uuid.uuid4().hex[:16]}"
        shop.refresh_token = f"mock_refresh_token_{uuid.uuid4().hex[:16]}"
        shop.token_expires_at = timezone.now() + timedelta(days=30)
        shop.status = 1
        shop.save()
        
        return Response({
            'message': '令牌刷新成功',
            'expires_at': shop.token_expires_at
        })
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """撤销授权"""
        shop = self.get_object()
        
        shop.auth_token = ''
        shop.refresh_token = ''
        shop.token_expires_at = None
        shop.status = 0  # 待授权
        shop.save()
        
        return Response({
            'message': '授权已撤销'
        })
    
    @action(detail=False, methods=['post'])
    def get_oauth_url(self, request):
        """获取OAuth授权URL（模拟）"""
        serializer = OAuthUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        platform_id = serializer.validated_data['platform_id']
        redirect_uri = serializer.validated_data.get('redirect_uri', 'http://localhost:5173/oauth/callback')
        
        try:
            platform = Platform.objects.get(id=platform_id)
        except Platform.DoesNotExist:
            return Response(
                {'error': '平台不存在'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mock OAuth URL
        state = uuid.uuid4().hex
        oauth_url = f"https://oauth.{platform.code}.com/authorize?"
        oauth_url += f"client_id=mock_client_id&"
        oauth_url += f"redirect_uri={redirect_uri}&"
        oauth_url += f"response_type=code&"
        oauth_url += f"state={state}&"
        oauth_url += f"scope=read,write"
        
        return Response({
            'oauth_url': oauth_url,
            'state': state,
            'platform': PlatformSerializer(platform).data
        })
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """同步店铺数据"""
        shop = self.get_object()
        
        serializer = ShopSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sync_type = serializer.validated_data['sync_type']
        
        # 检查授权状态
        if shop.status != 1:
            return Response(
                {'error': '店铺未授权，无法同步'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 更新同步状态
        shop.sync_status = 1  # 同步中
        shop.save()
        
        # Mock同步过程
        import time
        time.sleep(1)
        
        # 更新同步状态为完成
        shop.sync_status = 2  # 同步完成
        shop.last_sync_at = timezone.now()
        shop.save()
        
        return Response({
            'message': f'{sync_type}数据同步成功',
            'sync_type': sync_type,
            'sync_time': shop.last_sync_at
        })
    
    @action(detail=False, methods=['get'])
    def auth_status(self, request):
        """获取店铺授权状态统计"""
        tenant = request.tenant
        
        total = Shop.objects.filter(tenant=tenant).count()
        authorized = Shop.objects.filter(tenant=tenant, status=1).count()
        expired = Shop.objects.filter(tenant=tenant, status=2).count()
        pending = Shop.objects.filter(tenant=tenant, status=0).count()
        
        return Response({
            'total': total,
            'authorized': authorized,
            'expired': expired,
            'pending': pending
        })
