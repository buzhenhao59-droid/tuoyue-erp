from django.db import models


class SystemConfig(models.Model):
    """系统配置"""
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    
    config_key = models.CharField('配置键', max_length=100)
    config_value = models.TextField('配置值')
    config_type = models.CharField('值类型', max_length=20, default='string')  # string/int/float/bool/json
    
    description = models.CharField('描述', max_length=255, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
        db_table = 'system_configs'
        unique_together = ['tenant', 'config_key']


class OperationLog(models.Model):
    """操作日志"""
    ACTION_CHOICES = [
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('export', '导出'),
        ('import', '导入'),
        ('login', '登录'),
        ('logout', '登出'),
        ('other', '其他'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='用户')
    
    action = models.CharField('操作类型', max_length=20, choices=ACTION_CHOICES)
    module = models.CharField('操作模块', max_length=50)
    object_type = models.CharField('对象类型', max_length=50, blank=True)
    object_id = models.CharField('对象ID', max_length=50, blank=True)
    
    # 详情
    description = models.TextField('操作描述')
    old_data = models.JSONField('变更前数据', default=dict, blank=True)
    new_data = models.JSONField('变更后数据', default=dict, blank=True)
    
    # 请求信息
    ip_address = models.GenericIPAddressField('IP地址', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    request_path = models.CharField('请求路径', max_length=500, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        db_table = 'operation_logs'
        ordering = ['-created_at']


class ScheduledTask(models.Model):
    """定时任务"""
    TASK_TYPE_CHOICES = [
        ('sync_orders', '同步订单'),
        ('sync_inventory', '同步库存'),
        ('sync_products', '同步商品'),
        ('collection', '采集任务'),
        ('report', '生成报表'),
        ('backup', '数据备份'),
    ]
    
    STATUS_CHOICES = [
        (0, '待执行'),
        (1, '执行中'),
        (2, '成功'),
        (3, '失败'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    
    task_name = models.CharField('任务名称', max_length=100)
    task_type = models.CharField('任务类型', max_length=30, choices=TASK_TYPE_CHOICES)
    
    # 执行配置
    cron_expression = models.CharField('Cron表达式', max_length=50)
    is_enabled = models.BooleanField('是否启用', default=True)
    
    # 执行参数
    params = models.JSONField('执行参数', default=dict, blank=True)
    
    # 最后执行
    last_run_at = models.DateTimeField('最后执行时间', null=True, blank=True)
    last_run_status = models.SmallIntegerField('最后执行状态', default=0, choices=STATUS_CHOICES)
    last_run_result = models.TextField('最后执行结果', blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '定时任务'
        verbose_name_plural = '定时任务'
        db_table = 'scheduled_tasks'


class Notification(models.Model):
    """系统通知"""
    TYPE_CHOICES = [
        ('system', '系统通知'),
        ('order', '订单通知'),
        ('inventory', '库存预警'),
        ('finance', '财务通知'),
        ('task', '任务提醒'),
    ]
    
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, verbose_name='租户', null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='接收用户')
    
    title = models.CharField('标题', max_length=200)
    content = models.TextField('内容')
    notification_type = models.CharField('通知类型', max_length=20, choices=TYPE_CHOICES)
    
    # 链接
    link_type = models.CharField('链接类型', max_length=50, blank=True)
    link_id = models.CharField('链接ID', max_length=50, blank=True)
    
    # 状态
    is_read = models.BooleanField('是否已读', default=False)
    read_at = models.DateTimeField('阅读时间', null=True, blank=True)
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '系统通知'
        verbose_name_plural = '系统通知'
        db_table = 'notifications'
        ordering = ['-created_at']
