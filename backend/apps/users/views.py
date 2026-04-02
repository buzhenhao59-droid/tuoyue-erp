from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django_filters import rest_framework as filters

from apps.users.models import User, Role, UserRole
from apps.users.serializers import (
    UserSerializer, UserCreateSerializer, RoleSerializer, UserRoleSerializer,
    LoginSerializer, ChangePasswordSerializer
)


class UserFilter(filters.FilterSet):
    """用户过滤器"""
    is_active = filters.BooleanFilter(field_name='is_active')
    
    class Meta:
        model = User
        fields = ['is_active']


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    filterset_class = UserFilter
    
    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': '密码修改成功'})


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    serializer_class = RoleSerializer
    
    def get_queryset(self):
        return Role.objects.filter(tenant=self.request.tenant)


class UserRoleViewSet(viewsets.ModelViewSet):
    """用户角色关联视图集"""
    serializer_class = UserRoleSerializer
    
    def get_queryset(self):
        return UserRole.objects.filter(
            user__tenant=self.request.tenant
        ).select_related('user', 'role')


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': '用户已被禁用'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


@api_view(['POST'])
def logout(request):
    """用户登出"""
    # 这里可以添加token黑名单逻辑
    return Response({'message': '登出成功'})


@api_view(['GET'])
def get_user_info(request):
    """获取当前用户信息"""
    from apps.users.serializers import UserSerializer
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
