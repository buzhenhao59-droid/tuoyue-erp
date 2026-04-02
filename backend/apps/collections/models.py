"""
拓岳 ERP - 产品采集模型（妙手 ERP 深度克隆版）
支持复杂 SKU 存储、采集配置、图片本地化
"""

from django.db import models
import json


class CollectionConfig(models.Model):
    """采集配置（对应妙手的"采集设置"）"""
    
    # 价格转换设置
    PRICE_RULES = [
        ('fixed', '固定倍率'),
        ('tier', '阶梯倍率'),
        ('formula', '自定义公式'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    name = models.CharField('配置名称', max_length=100, default='默认配置')
    
    # 价格自动转换
    price_rule = models.CharField('价格规则', max_length=20, choices=PRICE_RULES, default='fixed')
    price_multiplier = models.DecimalField('价格倍率', max_digits=5, decimal_places=2, default=1.5,
                                          help_text='如 1.5 表示原价乘以 1.5')
    price_addition = models.DecimalField('固定加价', max_digits=10, decimal_places=2, default=0,
                                        help_text='在倍率基础上额外增加的金额')
    
    # 价格区间保护
    min_price = models.DecimalField('最低售价', max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField('最高售价', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # 内容处理
    auto_translate = models.BooleanField('自动翻译描述', default=False)
    translate_to = models.CharField('翻译目标语言', max_length=10, default='en',
                                   help_text='en:英语, th:泰语, vi:越南语等')
    
    # 图片处理
    download_images = models.BooleanField('自动下载图片', default=True)
    watermark_remove = models.BooleanField('自动去水印', default=False)
    image_compress = models.BooleanField('图片压缩', default=True)
    
    # SKU 默认设置
    default_sku_attrs = models.JSONField('默认SKU属性', default=list, blank=True,
                                        help_text='[{name: "颜色", values: ["红", "蓝"]}]')
    default_stock = models.IntegerField('默认库存', default=999)
    
    # 关键词过滤
    keyword_filter = models.JSONField('关键词过滤', default=dict, blank=True,
                                     help_text='{include: ["必须包含"], exclude: ["排除词"]}')
    
    # 类目映射
    category_mapping = models.JSONField('类目映射', default=dict, blank=True,
                                       help_text='{"1688类目ID": "目标类目ID"}')
    
    is_default = models.BooleanField('是否默认配置', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '采集配置'
        verbose_name_plural = '采集配置'
        db_table = 'collection_configs'
        
    def __str__(self):
        return self.name


class CollectionTask(models.Model):
    """采集任务（妙手多链接采集）"""
    
    TASK_TYPES = [
        ('link', '链接采集'),
        ('plugin', '插件采集'),
        ('api', 'API导入'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('processing', '执行中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('partial', '部分成功'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    config = models.ForeignKey(CollectionConfig, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='采集配置')
    
    # 任务信息
    task_no = models.CharField('任务编号', max_length=50, unique=True)
    task_type = models.CharField('任务类型', max_length=20, choices=TASK_TYPES, default='link')
    name = models.CharField('任务名称', max_length=200, blank=True)
    
    # 采集源
    source_urls = models.JSONField('采集链接列表', default=list,
                                  help_text='[{url: "链接", platform: "1688", status: "pending"}]')
    source_platform = models.CharField('来源平台', max_length=20, blank=True)
    
    # 统计
    total_count = models.IntegerField('总链接数', default=0)
    success_count = models.IntegerField('成功数', default=0)
    fail_count = models.IntegerField('失败数', default=0)
    
    # 状态
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    error_msg = models.TextField('错误信息', blank=True)
    retry_count = models.SmallIntegerField('重试次数', default=0)
    
    # 时间
    started_at = models.DateTimeField('开始时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '采集任务'
        verbose_name_plural = '采集任务'
        db_table = 'collection_tasks'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.task_no} - {self.name or '未命名任务'}"
    
    def save(self, *args, **kwargs):
        if not self.task_no:
            from datetime import datetime
            self.task_no = f"CJ{datetime.now().strftime('%Y%m%d%H%M%S')}{self.id or ''}"
        super().save(*args, **kwargs)


class CollectedProduct(models.Model):
    """采集商品（妙手产品列表）"""
    
    STATUS_CHOICES = [
        ('pending', '待认领'),
        ('claimed', '已认领'),
        ('editing', '编辑中'),
        ('published', '已发布'),
        ('ignored', '已忽略'),
        ('failed', '采集失败'),
    ]
    
    PLATFORM_COLORS = {
        '1688': '#FF6A00',
        'taobao': '#FF5000',
        'tmall': '#FF0036',
        'shopee': '#EE4D2D',
        'lazada': '#0F156D',
        'tiktok': '#000000',
    }
    
    # 基础关联
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    task = models.ForeignKey(CollectionTask, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='products', verbose_name='采集任务')
    config = models.ForeignKey(CollectionConfig, on_delete=models.SET_NULL, null=True, blank=True,
                              verbose_name='使用的配置')
    
    # 来源信息
    source_url = models.URLField('来源链接', max_length=1000)
    source_platform = models.CharField('来源平台', max_length=20)
    source_id = models.CharField('来源商品ID', max_length=100, blank=True, db_index=True)
    source_shop_id = models.CharField('来源店铺ID', max_length=100, blank=True)
    source_shop_name = models.CharField('来源店铺名', max_length=200, blank=True)
    
    # 采集状态
    collect_status = models.CharField('采集状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    collect_error = models.TextField('采集错误', blank=True)
    collect_time = models.DateTimeField('采集时间', null=True, blank=True)
    
    # 商品基础信息
    title = models.CharField('商品标题', max_length=500)
    title_en = models.CharField('英文标题', max_length=500, blank=True)
    description = models.TextField('商品描述', blank=True)
    description_en = models.TextField('英文描述', blank=True)
    
    # 图片（支持本地化缓存）
    main_image = models.URLField('主图URL', max_length=1000)
    main_image_local = models.CharField('本地主图路径', max_length=500, blank=True)
    images = models.JSONField('图片列表', default=list, help_text='原始图片URL列表')
    images_local = models.JSONField('本地图片列表', default=list, help_text='本地化后的图片路径')
    
    # 价格（原始 vs 转换后）
    original_price_min = models.DecimalField('原始最低价', max_digits=15, decimal_places=2, null=True)
    original_price_max = models.DecimalField('原始最高价', max_digits=15, decimal_places=2, null=True)
    price_min = models.DecimalField('转换后最低价', max_digits=15, decimal_places=2, null=True)
    price_max = models.DecimalField('转换后最高价', max_digits=15, decimal_places=2, null=True)
    currency = models.CharField('货币', max_length=10, default='CNY')
    
    # 类目
    source_category_id = models.CharField('来源类目ID', max_length=50, blank=True)
    source_category_name = models.CharField('来源类目名', max_length=200, blank=True)
    target_category_id = models.CharField('目标类目ID', max_length=50, blank=True)
    target_category_name = models.CharField('目标类目名', max_length=200, blank=True)
    
    # 属性
    brand = models.CharField('品牌', max_length=100, blank=True)
    material = models.CharField('材质', max_length=100, blank=True)
    origin = models.CharField('产地', max_length=50, blank=True)
    
    # 物流信息
    weight = models.DecimalField('重量(kg)', max_digits=10, decimal_places=3, null=True)
    length = models.DecimalField('长(cm)', max_digits=10, decimal_places=2, null=True)
    width = models.DecimalField('宽(cm)', max_digits=10, decimal_places=2, null=True)
    height = models.DecimalField('高(cm)', max_digits=10, decimal_places=2, null=True)
    
    # SKU 矩阵（妙手核心功能）
    sku_attributes = models.JSONField('SKU属性定义', default=list,
                                     help_text='[{id, name, values: [{id, name, image}]}]')
    skus = models.JSONField('SKU列表', default=list,
                           help_text='[{sku_id, attributes: {颜色: "红", 尺寸: "L"}, price, stock, image}]')
    sku_count = models.IntegerField('SKU数量', default=0)
    
    # 业务状态
    status = models.CharField('业务状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # 认领信息
    claimed_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='claimed_products', verbose_name='认领人')
    claimed_at = models.DateTimeField('认领时间', null=True, blank=True)
    claim_note = models.TextField('认领备注', blank=True)
    
    # 发布信息
    published_product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, 
                                         null=True, blank=True, verbose_name='发布的商品')
    published_shops = models.JSONField('发布到店铺', default=list,
                                      help_text='[{shop_id, platform, status, time}]')
    
    # 编辑信息
    editor = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='editing_products', verbose_name='编辑人')
    editing_at = models.DateTimeField('开始编辑时间', null=True, blank=True)
    
    # 原始数据备份
    raw_data = models.JSONField('原始采集数据', default=dict)
    
    # 时间戳
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '采集商品'
        verbose_name_plural = '采集商品'
        db_table = 'collected_products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['source_platform', 'source_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['claimed_by', 'status']),
        ]
        
    def __str__(self):
        return self.title[:50]
    
    @property
    def platform_color(self):
        """获取平台标识颜色"""
        return self.PLATFORM_COLORS.get(self.source_platform.lower(), '#999999')
    
    @property
    def platform_icon(self):
        """获取平台图标"""
        return f'/static/platforms/{self.source_platform.lower()}.svg'
    
    def get_price_display(self):
        """获取价格显示"""
        if self.price_min and self.price_max:
            if self.price_min == self.price_max:
                return f"¥{self.price_min}"
            return f"¥{self.price_min} - ¥{self.price_max}"
        return "暂无价格"
    
    def to_product_dict(self):
        """转换为商品字典（用于发布）"""
        return {
            'name': self.title_en or self.title,
            'description': self.description_en or self.description,
            'main_image': self.main_image_local or self.main_image,
            'images': self.images_local if self.images_local else self.images,
            'skus': self.skus,
            'weight': self.weight,
            'category_id': self.target_category_id,
        }


class CollectionPluginLog(models.Model):
    """插件采集日志"""
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    plugin_id = models.CharField('插件ID', max_length=100)
    plugin_version = models.CharField('插件版本', max_length=20)
    
    # 接收的数据
    payload = models.JSONField('接收数据')
    
    # 处理状态
    status = models.CharField('处理状态', max_length=20, default='pending')
    product = models.ForeignKey(CollectedProduct, on_delete=models.SET_NULL, null=True, blank=True)
    error_msg = models.TextField('错误信息', blank=True)
    
    # IP 记录
    ip_address = models.GenericIPAddressField('IP地址', null=True)
    user_agent = models.TextField('User-Agent', blank=True)
    
    created_at = models.DateTimeField('接收时间', auto_now_add=True)
    processed_at = models.DateTimeField('处理时间', null=True, blank=True)
    
    class Meta:
        verbose_name = '插件采集日志'
        verbose_name_plural = '插件采集日志'
        db_table = 'collection_plugin_logs'
        ordering = ['-created_at']
