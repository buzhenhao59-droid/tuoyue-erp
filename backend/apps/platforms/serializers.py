from rest_framework import serializers
from apps.platforms.models import Platform, Shop


class PlatformSerializer(serializers.ModelSerializer):
    """电商平台序列化器"""
    
    class Meta:
        model = Platform
        fields = '__all__'


class ShopListSerializer(serializers.ModelSerializer):
    """店铺列表序列化器"""
    platform_name = serializers.CharField(source='platform.name', read_only=True)
    platform_icon = serializers.URLField(source='platform.icon', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sync_status_display = serializers.CharField(source='get_sync_status_display', read_only=True)
    
    class Meta:
        model = Shop
        fields = [
            'id', 'platform', 'platform_name', 'platform_icon',
            'name', 'shop_code', 'platform_shop_id',
            'status', 'status_display', 'sync_status', 'sync_status_display',
            'last_sync_at', 'created_at'
        ]


class ShopDetailSerializer(serializers.ModelSerializer):
    """店铺详情序列化器"""
    platform = PlatformSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sync_status_display = serializers.CharField(source='get_sync_status_display', read_only=True)
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    
    class Meta:
        model = Shop
        fields = '__all__'
        read_only_fields = ['tenant', 'auth_token', 'refresh_token', 'token_expires_at']


class ShopCreateSerializer(serializers.ModelSerializer):
    """店铺创建序列化器"""
    
    class Meta:
        model = Shop
        fields = ['platform', 'name', 'shop_code', 'settings']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        validated_data['creator'] = self.context['request'].user
        validated_data['status'] = 0  # 待授权
        return super().create(validated_data)


class ShopAuthSerializer(serializers.Serializer):
    """店铺授权序列化器"""
    auth_code = serializers.CharField(max_length=255)
    
    def validate_auth_code(self, value):
        if not value:
            raise serializers.ValidationError('授权码不能为空')
        return value


class OAuthUrlSerializer(serializers.Serializer):
    """OAuth授权URL序列化器"""
    platform_id = serializers.IntegerField()
    redirect_uri = serializers.URLField(required=False)
    
    def validate_platform_id(self, value):
        try:
            Platform.objects.get(id=value)
        except Platform.DoesNotExist:
            raise serializers.ValidationError('平台不存在')
        return value


class ShopSyncSerializer(serializers.Serializer):
    """店铺同步序列化器"""
    sync_type = serializers.ChoiceField(
        choices=[
            ('orders', '订单'),
            ('products', '商品'),
            ('inventory', '库存'),
        ],
        default='orders'
    )
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
