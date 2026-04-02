from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.tenants.models import Tenant
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """自定义用户模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    username = models.CharField('用户名', max_length=50, unique=True)
    email = models.EmailField('邮箱', max_length=100, blank=True)
    phone = models.CharField('手机号', max_length=20, blank=True)
    real_name = models.CharField('真实姓名', max_length=50, blank=True)
    avatar = models.URLField('头像', blank=True)
    
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    is_superuser = models.BooleanField('是否超级管理员', default=False)
    
    last_login = models.DateTimeField('最后登录时间', blank=True, null=True)
    date_joined = models.DateTimeField('注册时间', default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Role(models.Model):
    """角色模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='租户')
    name = models.CharField('角色名称', max_length=50)
    code = models.CharField('角色编码', max_length=50)
    description = models.CharField('描述', max_length=255, blank=True)
    permissions = models.JSONField('权限列表', default=list)
    status = models.BooleanField('状态', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    
    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'roles'
        unique_together = ['tenant', 'code']
    
    def __str__(self):
        return self.name


class UserRole(models.Model):
    """用户角色关联"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='角色')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
        db_table = 'user_roles'
        unique_together = ['user', 'role']
