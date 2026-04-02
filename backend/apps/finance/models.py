from django.db import models


class Transaction(models.Model):
    """交易流水"""
    BIZ_TYPE_CHOICES = [
        ('order', '订单'),
        ('purchase', '采购'),
        ('refund', '退款'),
        ('other', '其他'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    transaction_no = models.CharField('交易单号', max_length=50, unique=True)
    biz_type = models.CharField('业务类型', max_length=20, choices=BIZ_TYPE_CHOICES)
    biz_id = models.BigIntegerField('业务单ID', null=True, blank=True)
    biz_no = models.CharField('业务单号', max_length=50, blank=True)
    
    type = models.CharField('类型', max_length=10)  # income-收入 expense-支出
    amount = models.DecimalField('金额', max_digits=12, decimal_places=2, default=0)
    currency = models.CharField('币种', max_length=10, default='USD')
    description = models.CharField('描述', max_length=255, blank=True)
    status = models.SmallIntegerField('状态', default=1)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '交易流水'
        verbose_name_plural = '交易流水'
        db_table = 'transactions'
