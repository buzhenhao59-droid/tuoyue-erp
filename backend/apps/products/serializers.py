from rest_framework import serializers
from apps.products.models import ProductCategory, Product, ProductSKU, ProductPlatformMapping


class ProductCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'parent', 'name', 'code', 'level', 'sort_order', 'status', 'children', 'created_at']
        read_only_fields = ['tenant']
    
    def get_children(self, obj):
        if hasattr(obj, 'children'):
            return ProductCategorySerializer(obj.children.all(), many=True).data
        return []
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class ProductSKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    
    class Meta:
        model = ProductSKU
        fields = [
            'id', 'sku_code', 'barcode', 'spec_info', 'spec_image',
            'purchase_price', 'cost_price', 'sale_price', 'market_price',
            'weight', 'status', 'created_at'
        ]
        read_only_fields = ['tenant']


class ProductListSerializer(serializers.ModelSerializer):
    """商品列表序列化器"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sku_count = serializers.IntegerField(source='skus.count', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'spu_code', 'name', 'name_en', 'main_image',
            'category', 'category_name', 'status', 'status_display',
            'sku_count', 'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """商品详情序列化器"""
    category = ProductCategorySerializer(read_only=True)
    skus = ProductSKUSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):
    """商品创建序列化器"""
    skus = ProductSKUSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = [
            'category', 'spu_code', 'name', 'name_en', 'description', 'description_en',
            'brand', 'main_image', 'images', 'weight', 'length', 'width', 'height',
            'material', 'origin', 'hs_code', 'skus'
        ]
    
    def create(self, validated_data):
        skus_data = validated_data.pop('skus', [])
        validated_data['tenant'] = self.context['request'].tenant
        validated_data['creator'] = self.context['request'].user
        
        product = Product.objects.create(**validated_data)
        
        # 创建SKU
        for sku_data in skus_data:
            ProductSKU.objects.create(
                tenant=product.tenant,
                product=product,
                **sku_data
            )
        
        return product


class ProductPlatformMappingSerializer(serializers.ModelSerializer):
    """商品平台映射序列化器"""
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    platform_name = serializers.CharField(source='shop.platform.name', read_only=True)
    listing_status_display = serializers.CharField(source='get_listing_status_display', read_only=True)
    
    class Meta:
        model = ProductPlatformMapping
        fields = [
            'id', 'product', 'sku', 'shop', 'shop_name', 'platform_name',
            'platform_product_id', 'platform_sku_id', 'platform_listing_id',
            'listing_status', 'listing_status_display', 'last_listed_at', 'last_sync_at'
        ]
        read_only_fields = ['tenant']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)
