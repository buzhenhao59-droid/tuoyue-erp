from django.db import models


class LogisticsCompany(models.Model):
    """物流公司"""
    code = models.CharField('公司编码', max_length=50, unique=True)
    name = models.CharField('公司名称', max_length=100)
    name_en = models.CharField('英文名称', max_length=100, blank=True)
    company_type = models.CharField('类型', max_length=20, default='express')
    website = models.URLField('官网', blank=True)
    tracking_url = models.URLField('查询网址', blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    supported_countries = models.JSONField('支持国家', default=list, blank=True)
    status = models.BooleanField('状态', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '物流公司'
        verbose_name_plural = '物流公司'
        db_table = 'logistics_companies'


class ShippingMethod(models.Model):
    """物流渠道"""
    METHOD_TYPE_CHOICES = [
        ('standard', '标准快递'),
        ('express', '特快专递'),
        ('economy', '经济快递'),
        ('sea', '海运'),
        ('air', '空运'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    company = models.ForeignKey(LogisticsCompany, on_delete=models.CASCADE, verbose_name='物流公司')
    name = models.CharField('渠道名称', max_length=100)
    code = models.CharField('渠道编码', max_length=50)
    method_type = models.CharField('运输方式', max_length=20, choices=METHOD_TYPE_CHOICES)
    status = models.BooleanField('状态', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '物流渠道'
        verbose_name_plural = '物流渠道'
        db_table = 'shipping_methods'
