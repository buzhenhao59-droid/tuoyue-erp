"""
采集模块序列化器（妙手 ERP 深度克隆版）
"""

from rest_framework import serializers
from .models import CollectionConfig, CollectionTask, CollectedProduct, CollectionPluginLog


class CollectionConfigSerializer(serializers.ModelSerializer):
    """采集配置序列化器"""
    
    class Meta:
        model = CollectionConfig
        fields = [
            'id', 'name', 'price_rule', 'price_multiplier', 'price_addition',
            'min_price', 'max_price', 'auto_translate', 'translate_to',
            'download_images', 'watermark_remove', 'image_compress',
            'default_sku_attrs', 'default_stock', 'keyword_filter',
            'category_mapping', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CollectionConfigSimpleSerializer(serializers.ModelSerializer):
    """采集配置简版序列化器"""
    
    class Meta:
        model = CollectionConfig
        fields = ['id', 'name', 'is_default']


class CollectionTaskCreateSerializer(serializers.ModelSerializer):
    """创建采集任务序列化器"""
    urls_text = serializers.CharField(write_only=True, required=False,
                                     help_text='多行链接文本')
    
    class Meta:
        model = CollectionTask
        fields = ['config', 'name', 'urls_text', 'task_type']
    
    def create(self, validated_data):
        urls_text = validated_data.pop('urls_text', '')
        task_type = validated_data.get('task_type', 'link')
        
        # 解析链接
        source_urls = []
        if urls_text:
            for line in urls_text.split('\n'):
                url = line.strip()
                if url:
                    # 自动检测平台
                    platform = self._detect_platform(url)
                    source_urls.append({
                        'url': url,
                        'platform': platform,
                        'status': 'pending'
                    })
        
        validated_data['source_urls'] = source_urls
        validated_data['total_count'] = len(source_urls)
        
        return super().create(validated_data)
    
    def _detect_platform(self, url):
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


class CollectionTaskSerializer(serializers.ModelSerializer):
    """采集任务序列化器"""
    config_name = serializers.CharField(source='config.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    progress_percent = serializers.SerializerMethodField()
    
    class Meta:
        model = CollectionTask
        fields = [
            'id', 'task_no', 'task_type', 'name', 'config', 'config_name',
            'source_urls', 'source_platform', 'total_count', 'success_count',
            'fail_count', 'status', 'error_msg', 'retry_count', 'progress_percent',
            'started_at', 'completed_at', 'created_at', 'user', 'user_name'
        ]
        read_only_fields = [
            'task_no', 'source_platform', 'total_count', 'success_count',
            'fail_count', 'status', 'error_msg', 'retry_count',
            'started_at', 'completed_at', 'created_at'
        ]
    
    def get_progress_percent(self, obj):
        if obj.total_count == 0:
            return 0
        return int((obj.success_count + obj.fail_count) / obj.total_count * 100)


class CollectedProductListSerializer(serializers.ModelSerializer):
    """采集商品列表序列化器"""
    platform_color = serializers.CharField(read_only=True)
    platform_icon = serializers.CharField(read_only=True)
    price_display = serializers.CharField(source='get_price_display', read_only=True)
    claimed_by_name = serializers.CharField(source='claimed_by.username', read_only=True)
    
    class Meta:
        model = CollectedProduct
        fields = [
            'id', 'source_url', 'source_platform', 'platform_color', 'platform_icon',
            'main_image', 'title', 'price_display', 'price_min', 'price_max',
            'currency', 'sku_count', 'status', 'claimed_by_name', 'claimed_at',
            'created_at'
        ]


class CollectedProductDetailSerializer(serializers.ModelSerializer):
    """采集商品详情序列化器"""
    platform_color = serializers.CharField(read_only=True)
    platform_icon = serializers.CharField(read_only=True)
    price_display = serializers.CharField(source='get_price_display', read_only=True)
    claimed_by_name = serializers.CharField(source='claimed_by.username', read_only=True)
    editor_name = serializers.CharField(source='editor.username', read_only=True)
    task_no = serializers.CharField(source='task.task_no', read_only=True)
    
    class Meta:
        model = CollectedProduct
        fields = [
            'id', 'task_no', 'source_url', 'source_platform', 'source_id',
            'platform_color', 'platform_icon', 'collect_status', 'collect_error',
            'title', 'title_en', 'description', 'description_en',
            'main_image', 'main_image_local', 'images', 'images_local',
            'original_price_min', 'original_price_max', 'price_min', 'price_max',
            'price_display', 'currency', 'source_category_name', 'target_category_id',
            'target_category_name', 'brand', 'material', 'origin',
            'weight', 'length', 'width', 'height',
            'sku_attributes', 'skus', 'sku_count',
            'status', 'claimed_by', 'claimed_by_name', 'claimed_at', 'claim_note',
            'editor', 'editor_name', 'editing_at',
            'published_shops', 'raw_data', 'created_at', 'updated_at'
        ]


class CollectedProductUpdateSerializer(serializers.ModelSerializer):
    """采集商品更新序列化器（编辑用）"""
    
    class Meta:
        model = CollectedProduct
        fields = [
            'title_en', 'description_en', 'price_min', 'price_max',
            'target_category_id', 'target_category_name',
            'skus', 'images_local'
        ]


class BatchUpdatePriceSerializer(serializers.Serializer):
    """批量修改价格序列化器"""
    ids = serializers.ListField(child=serializers.IntegerField())
    price_type = serializers.ChoiceField(choices=['fixed', 'multiplier', 'addition'])
    value = serializers.DecimalField(max_digits=10, decimal_places=2)


class BatchPushToShopSerializer(serializers.Serializer):
    """批量推送到店铺序列化器"""
    ids = serializers.ListField(child=serializers.IntegerField())
    shop_ids = serializers.ListField(child=serializers.IntegerField())
    config_id = serializers.IntegerField(required=False, allow_null=True)


class PluginWebhookSerializer(serializers.Serializer):
    """插件 Webhook 序列化器"""
    plugin_id = serializers.CharField()
    plugin_version = serializers.CharField(default='1.0.0')
    url = serializers.URLField()
    platform = serializers.CharField()
    data = serializers.DictField()


class CollectionStatsSerializer(serializers.Serializer):
    """采集统计序列化器"""
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    claimed = serializers.IntegerField()
    editing = serializers.IntegerField()
    published = serializers.IntegerField()
    ignored = serializers.IntegerField()
    failed = serializers.IntegerField()
    by_platform = serializers.DictField()
