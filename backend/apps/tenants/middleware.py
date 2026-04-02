class TenantMiddleware:
    """租户中间件 - 自动设置当前租户"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 从用户获取租户
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.tenant = getattr(request.user, 'tenant', None)
        else:
            request.tenant = None
        
        response = self.get_response(request)
        return response
