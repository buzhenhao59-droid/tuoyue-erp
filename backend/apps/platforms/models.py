from django.db import models


class Platform(models.Model):
    """电商平台"""
    name = models.CharField('平台名称', max_length=50)
    code = models.CharField('平台编码', max_length=20, unique=True)
    icon = models.URLField('图标', blank=True)
    website = models.URLField('官网', blank=True)
    api_base_url = models.URLField('API地址', blank=True)
    auth_type = models.CharField('认证类型', max_length=20, default='oauth')
    status = models.BooleanField('状态', default=True)
    sort_order = models.IntegerField('排序', default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '电商平台'
        verbose_name_plural = '电商平台'
        db_table = 'platforms'
    
    def __str__(self):
        return self.name


class Shop(models.Model):
    """店铺"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, verbose_name='平台')
    name = models.CharField('店铺名称', max_length=100)
    shop_code = models.CharField('店铺编码', max_length=50, blank=True)
    platform_shop_id = models.CharField('平台店铺ID', max_length=100, blank=True)
    
    # 授权信息
    auth_token = models.TextField('授权令牌', blank=True)
    refresh_token = models.TextField('刷新令牌', blank=True)
    token_expires_at = models.DateTimeField('令牌过期时间', null=True, blank=True)
    
    status = models.SmallIntegerField('状态', default=1)  # 0-禁用 1-启用 2-授权过期
    sync_status = models.SmallIntegerField('同步状态', default=0)  # 0-未同步 1-同步中 2-同步完成
    last_sync_at = models.DateTimeField('最后同步时间', null=True, blank=True)
    settings = models.JSONField('配置', default=dict, blank=True)
    
    creator = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        db_table = 'shops'
    
    def __str__(self):
        return f'{self.platform.name} - {self.name}'
