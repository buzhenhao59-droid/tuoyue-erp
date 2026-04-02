from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import Role, UserRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'real_name', 'avatar',
            'tenant', 'tenant_name', 'is_staff', 'is_active',
            'last_login', 'date_joined'
        ]
        read_only_fields = ['tenant']


class UserCreateSerializer(serializers.ModelSerializer):
    """用户创建序列化器"""
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'real_name', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['tenant'] = self.context['request'].tenant
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'status', 'created_at']
        read_only_fields = ['tenant']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)


class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'user_name', 'role', 'role_name', 'created_at']


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
