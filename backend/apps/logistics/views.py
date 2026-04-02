from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import LogisticsCompany, ShippingMethod
from .serializers import LogisticsCompanySerializer, ShippingMethodSerializer


class LogisticsCompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """物流公司视图集"""
    permission_classes = [IsAuthenticated]
    queryset = LogisticsCompany.objects.filter(status=True)
    serializer_class = LogisticsCompanySerializer


class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    """物流渠道视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = ShippingMethodSerializer
    
    def get_queryset(self):
        return ShippingMethod.objects.filter(tenant=self.request.tenant, status=True)
