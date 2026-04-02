from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.views import UserViewSet, RoleViewSet, UserRoleViewSet, login, logout, get_user_info

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('user/', get_user_info, name='user-info'),
]
