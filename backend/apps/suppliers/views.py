from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Supplier, PurchaseOrder
from .serializers import SupplierSerializer, PurchaseOrderSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    """供应商视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer
    
    def get_queryset(self):
        return Supplier.objects.filter(tenant=self.request.tenant)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """采购订单视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = PurchaseOrderSerializer
    
    def get_queryset(self):
        return PurchaseOrder.objects.filter(tenant=self.request.tenant).select_related('supplier', 'warehouse')
