from django.db import models


class Tenant(models.Model):
    """租户模型 - SAAS多租户基础"""
    name = models.CharField('租户名称', max_length=100)
    code = models.CharField('租户编码', max_length=50, unique=True)
    status = models.BooleanField('状态', default=True)
    plan = models.CharField('套餐', max_length=20, default='basic')
    expired_at = models.DateTimeField('到期时间', blank=True, null=True)
    
    contact_name = models.CharField('联系人', max_length=50, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True)
    contact_email = models.EmailField('联系邮箱', max_length=100, blank=True)
    
    settings = models.JSONField('租户配置', default=dict, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '租户'
        verbose_name_plural = '租户'
        db_table = 'tenants'
    
    def __str__(self):
        return self.name
