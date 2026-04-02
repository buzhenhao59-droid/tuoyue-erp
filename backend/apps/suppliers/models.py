from django.db import models


class Supplier(models.Model):
    """供应商"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    name = models.CharField('供应商名称', max_length=100)
    code = models.CharField('供应商编码', max_length=50, blank=True)
    contact_person = models.CharField('联系人', max_length=50, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    contact_email = models.EmailField('联系邮箱', blank=True)
    address = models.CharField('地址', max_length=255, blank=True)
    website = models.URLField('网站', blank=True)
    status = models.SmallIntegerField('状态', default=1)  # 0-禁用 1-启用
    remark = models.TextField('备注', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = '供应商'
        db_table = 'suppliers'


class PurchaseOrder(models.Model):
    """采购订单"""
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('pending', '待确认'),
        ('confirmed', '已确认'),
        ('received', '已收货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    po_no = models.CharField('采购单号', max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    warehouse = models.ForeignKey('inventory.Warehouse', on_delete=models.CASCADE, verbose_name='入库仓库')
    
    status = models.CharField('状态', max_length=20, default='draft', choices=STATUS_CHOICES)
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2, default=0)
    total_quantity = models.IntegerField('总数量', default=0)
    remark = models.TextField('备注', blank=True)
    
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    confirmed_at = models.DateTimeField('确认时间', null=True, blank=True)
    received_at = models.DateTimeField('收货时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '采购订单'
        verbose_name_plural = '采购订单'
        db_table = 'purchase_orders'


class PurchaseOrderItem(models.Model):
    """采购订单明细"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='采购单')
    sku = models.ForeignKey('products.ProductSKU', on_delete=models.CASCADE, verbose_name='SKU')
    
    quantity = models.IntegerField('采购数量', default=0)
    received_quantity = models.IntegerField('已收货数量', default=0)
    unit_price = models.DecimalField('单价', max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField('总价', max_digits=12, decimal_places=2, default=0)
    remark = models.CharField('备注', max_length=255, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '采购明细'
        verbose_name_plural = '采购明细'
        db_table = 'purchase_order_items'
