from django.db import models


class Warehouse(models.Model):
    """仓库"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    name = models.CharField('仓库名称', max_length=100)
    code = models.CharField('仓库编码', max_length=50)
    type = models.CharField('类型', max_length=20, default='self')  # self-自营 third-第三方
    
    country = models.CharField('国家', max_length=50, blank=True)
    province = models.CharField('省/州', max_length=50, blank=True)
    city = models.CharField('城市', max_length=50, blank=True)
    address = models.CharField('详细地址', max_length=255, blank=True)
    contact_name = models.CharField('联系人', max_length=50, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    
    status = models.SmallIntegerField('状态', default=1)  # 0-禁用 1-启用
    is_default = models.BooleanField('是否默认', default=False)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = '仓库'
        db_table = 'warehouses'
        unique_together = ['tenant', 'code']


class Inventory(models.Model):
    """库存"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    sku = models.ForeignKey('products.ProductSKU', on_delete=models.CASCADE, verbose_name='SKU')
    
    quantity = models.IntegerField('可用库存', default=0)
    locked_quantity = models.IntegerField('锁定库存', default=0)
    warning_threshold = models.IntegerField('预警阈值', default=10)
    status = models.SmallIntegerField('状态', default=1)
    
    last_check_at = models.DateTimeField('最后盘点时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '库存'
        verbose_name_plural = '库存'
        db_table = 'inventories'
        unique_together = ['warehouse', 'sku']


class InventoryLog(models.Model):
    """库存流水"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    sku = models.ForeignKey('products.ProductSKU', on_delete=models.CASCADE, verbose_name='SKU')
    
    type = models.CharField('类型', max_length=20)  # in-入库 out-出库 adjust-调整
    quantity = models.IntegerField('变动数量')  # 正数增加,负数减少
    before_qty = models.IntegerField('变动前数量')
    after_qty = models.IntegerField('变动后数量')
    
    biz_type = models.CharField('业务类型', max_length=50, blank=True)  # purchase/sale/return
    biz_no = models.CharField('业务单号', max_length=50, blank=True)
    remark = models.CharField('备注', max_length=255, blank=True)
    operator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '库存流水'
        verbose_name_plural = '库存流水'
        db_table = 'inventory_logs'
