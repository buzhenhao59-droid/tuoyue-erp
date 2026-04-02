from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db.models import Q

from apps.products.models import ProductCategory, Product, ProductSKU, ProductPlatformMapping
from apps.products.serializers import (
    ProductCategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ProductSKUSerializer, ProductPlatformMappingSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """商品分类视图集"""
    serializer_class = ProductCategorySerializer
    
    def get_queryset(self):
        return ProductCategory.objects.filter(
            tenant=self.request.tenant,
            parent=None  # 只返回顶级分类
        ).prefetch_related('children')


class ProductFilter(filters.FilterSet):
    """商品过滤器"""
    category = filters.NumberFilter(field_name='category_id')
    status = filters.NumberFilter(field_name='status')
    
    class Meta:
        model = Product
        fields = ['category', 'status']


class ProductViewSet(viewsets.ModelViewSet):
    """商品管理视图集"""
    filterset_class = ProductFilter
    
    def get_queryset(self):
        queryset = Product.objects.filter(tenant=self.request.tenant)
        
        # 搜索
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(spu_code__icontains=search) |
                Q(name_en__icontains=search)
            )
        
        return queryset.select_related('category').prefetch_related('skus')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductDetailSerializer


class ProductSKUViewSet(viewsets.ModelViewSet):
    """SKU管理视图集"""
    serializer_class = ProductSKUSerializer
    
    def get_queryset(self):
        return ProductSKU.objects.filter(tenant=self.request.tenant)


class ProductPlatformMappingViewSet(viewsets.ModelViewSet):
    """商品平台映射视图集"""
    serializer_class = ProductPlatformMappingSerializer
    
    def get_queryset(self):
        return ProductPlatformMapping.objects.filter(
            tenant=self.request.tenant
        ).select_related('shop', 'shop__platform')
