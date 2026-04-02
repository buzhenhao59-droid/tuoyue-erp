from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status


class CustomTokenObtainPairView(TokenObtainPairView):
    """自定义登录视图 - 统一响应格式"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({
                'code': 400,
                'message': '用户名或密码错误',
                'errors': {'detail': str(e)}
            }, status=status.HTTP_200_OK)
        
        return Response({
            'code': 200,
            'message': '登录成功',
            'data': serializer.validated_data
        })
