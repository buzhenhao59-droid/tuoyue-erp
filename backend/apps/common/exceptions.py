from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """自定义异常处理"""
    response = exception_handler(exc, context)
    
    if response is not None:
        # 统一错误格式
        error_data = {
            'code': response.status_code,
            'message': response.data.get('detail', '请求失败'),
            'errors': response.data if 'detail' not in response.data else None,
        }
        response.data = error_data
    else:
        # 处理未捕获的异常
        response = Response(
            {
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': '服务器内部错误',
                'errors': str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
