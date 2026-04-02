from django.db import models


class ProductCategory(models.Model):
    """商品分类"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='父分类')
    name = models.CharField('分类名称', max_length=100)
    code = models.CharField('分类编码', max_length=50, blank=True)
    level = models.SmallIntegerField('层级', default=1)
    sort_order = models.IntegerField('排序', default=0)
    status = models.BooleanField('状态', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '商品分类'
        verbose_name_plural = '商品分类'
        db_table = 'product_categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """商品SPU"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    spu_code = models.CharField('SPU编码', max_length=50)
    name = models.CharField('商品名称', max_length=255)
    name_en = models.CharField('英文名称', max_length=255, blank=True)
    description = models.TextField('商品描述', blank=True)
    description_en = models.TextField('英文描述', blank=True)
    brand = models.CharField('品牌', max_length=50, blank=True)
    
    # 图片
    main_image = models.URLField('主图', blank=True)
    images = models.JSONField('图片列表', default=list, blank=True)
    
    # 规格
    weight = models.DecimalField('重量(kg)', max_digits=10, decimal_places=3, null=True, blank=True)
    length = models.DecimalField('长(cm)', max_digits=10, decimal_places=2, null=True, blank=True)
    width = models.DecimalField('宽(cm)', max_digits=10, decimal_places=2, null=True, blank=True)
    height = models.DecimalField('高(cm)', max_digits=10, decimal_places=2, null=True, blank=True)
    material = models.CharField('材质', max_length=100, blank=True)
    origin = models.CharField('产地', max_length=50, blank=True)
    hs_code = models.CharField('海关编码', max_length=20, blank=True)
    
    status = models.SmallIntegerField('状态', default=0)  # 0-草稿 1-上架 2-下架
    source_type = models.CharField('来源', max_length=20, blank=True)  # manual/collection/import
    source_url = models.URLField('来源URL', blank=True)
    
    creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        db_table = 'products'
        unique_together = ['tenant', 'spu_code']
    
    def __str__(self):
        return self.name


class ProductSKU(models.Model):
    """商品SKU"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus', verbose_name='商品')
    sku_code = models.CharField('SKU编码', max_length=50)
    barcode = models.CharField('条形码', max_length=50, blank=True)
    spec_info = models.JSONField('规格信息', default=dict)  # {"颜色": "黑色", "尺寸": "XL"}
    spec_image = models.URLField('规格图片', blank=True)
    
    # 价格
    purchase_price = models.DecimalField('采购价', max_digits=12, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField('成本价', max_digits=12, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField('销售价', max_digits=12, decimal_places=2, null=True, blank=True)
    market_price = models.DecimalField('市场价', max_digits=12, decimal_places=2, null=True, blank=True)
    
    weight = models.DecimalField('重量(kg)', max_digits=10, decimal_places=3, null=True, blank=True)
    status = models.SmallIntegerField('状态', default=1)  # 0-禁用 1-启用
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = 'SKU'
        verbose_name_plural = 'SKU'
        db_table = 'product_skus'
        unique_together = ['tenant', 'sku_code']
    
    def __str__(self):
        return f'{self.product.name} - {self.sku_code}'


class ProductPlatformMapping(models.Model):
    """商品平台映射 - 多平台刊登"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品')
    sku = models.ForeignKey(ProductSKU, on_delete=models.CASCADE, null=True, blank=True, verbose_name='SKU')
    shop = models.ForeignKey('platforms.Shop', on_delete=models.CASCADE, verbose_name='店铺')
    
    platform_product_id = models.CharField('平台商品ID', max_length=100, blank=True)
    platform_sku_id = models.CharField('平台SKU ID', max_length=100, blank=True)
    platform_listing_id = models.CharField('平台刊登ID', max_length=100, blank=True)
    
    listing_status = models.SmallIntegerField('刊登状态', default=0)  # 0-未刊登 1-刊登中 2-已刊登 3-刊登失败
    listing_data = models.JSONField('刊登数据', default=dict, blank=True)
    last_listed_at = models.DateTimeField('最后刊登时间', null=True, blank=True)
    last_sync_at = models.DateTimeField('最后同步时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '平台映射'
        verbose_name_plural = '平台映射'
        db_table = 'product_platform_mappings'
        unique_together = ['sku', 'shop']
