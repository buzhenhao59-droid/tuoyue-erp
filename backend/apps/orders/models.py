from django.db import models


class Order(models.Model):
    """订单主表"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('paid', '已付款'),
        ('shipped', '已发货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    order_no = models.CharField('系统订单号', max_length=50, unique=True)
    platform_order_no = models.CharField('平台订单号', max_length=100)
    shop = models.ForeignKey('platforms.Shop', on_delete=models.CASCADE, verbose_name='店铺')
    platform_id = models.IntegerField('平台ID')
    
    status = models.CharField('状态', max_length=20, default='pending', choices=STATUS_CHOICES)
    order_status = models.CharField('平台原始状态', max_length=50, blank=True)
    
    currency = models.CharField('币种', max_length=10, default='USD')
    total_amount = models.DecimalField('订单总金额', max_digits=12, decimal_places=2, default=0)
    product_amount = models.DecimalField('商品金额', max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField('运费', max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField('优惠金额', max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField('税费', max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField('实付金额', max_digits=12, decimal_places=2, default=0)
    
    # 买家信息
    buyer_id = models.CharField('买家ID', max_length=100, blank=True)
    buyer_name = models.CharField('买家名称', max_length=100, blank=True)
    buyer_email = models.EmailField('买家邮箱', blank=True)
    buyer_phone = models.CharField('买家电话', max_length=50, blank=True)
    
    # 收件人信息
    receiver_name = models.CharField('收件人', max_length=100, blank=True)
    receiver_phone = models.CharField('收件电话', max_length=50, blank=True)
    receiver_country = models.CharField('国家', max_length=50, blank=True)
    receiver_province = models.CharField('省/州', max_length=100, blank=True)
    receiver_city = models.CharField('城市', max_length=100, blank=True)
    receiver_district = models.CharField('区/县', max_length=100, blank=True)
    receiver_address = models.CharField('详细地址', max_length=500, blank=True)
    receiver_zipcode = models.CharField('邮编', max_length=20, blank=True)
    
    remark = models.TextField('订单备注', blank=True)
    buyer_message = models.TextField('买家留言', blank=True)
    seller_memo = models.TextField('卖家备注', blank=True)
    
    paid_at = models.DateTimeField('付款时间', null=True, blank=True)
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    synced_at = models.DateTimeField('同步时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        db_table = 'orders'
        unique_together = ['shop', 'platform_order_no']


class OrderItem(models.Model):
    """订单商品明细"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='订单')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='商品')
    sku = models.ForeignKey('products.ProductSKU', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='SKU')
    
    platform_product_id = models.CharField('平台商品ID', max_length=100, blank=True)
    platform_sku_id = models.CharField('平台SKU ID', max_length=100, blank=True)
    product_name = models.CharField('商品名称', max_length=255)
    sku_name = models.CharField('SKU规格', max_length=255, blank=True)
    image = models.URLField('商品图片', blank=True)
    
    quantity = models.IntegerField('数量', default=1)
    unit_price = models.DecimalField('单价', max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField('总价', max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField('成本价', max_digits=12, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField('重量', max_digits=10, decimal_places=3, null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = '订单商品'
        db_table = 'order_items'


class OrderShipment(models.Model):
    """订单物流信息"""
    STATUS_CHOICES = [
        ('pending', '待发货'),
        ('shipped', '已发货'),
        ('delivered', '已签收'),
        ('returned', '已退回'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户', related_name='order_shipments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments', verbose_name='订单')
    tracking_no = models.CharField('物流单号', max_length=100)
    
    carrier_id = models.IntegerField('物流商ID', null=True, blank=True)
    carrier_name = models.CharField('物流商名称', max_length=50, blank=True)
    carrier_code = models.CharField('物流商编码', max_length=50, blank=True)
    shipping_method = models.CharField('运输方式', max_length=50, blank=True)
    
    status = models.CharField('状态', max_length=20, default='pending', choices=STATUS_CHOICES)
    weight = models.DecimalField('包裹重量', max_digits=10, decimal_places=3, null=True, blank=True)
    shipping_fee = models.DecimalField('实际运费', max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_delivery = models.DateField('预计送达', null=True, blank=True)
    
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    delivered_at = models.DateTimeField('送达时间', null=True, blank=True)
    tracking_data = models.JSONField('物流轨迹', default=list, blank=True)
    last_sync_at = models.DateTimeField('最后同步时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '订单物流'
        verbose_name_plural = '订单物流'
        db_table = 'order_shipments'
