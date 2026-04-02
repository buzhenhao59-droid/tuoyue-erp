from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Warehouse, Inventory
from .serializers import WarehouseSerializer, InventorySerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    """仓库视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = WarehouseSerializer
    
    def get_queryset(self):
        return Warehouse.objects.filter(tenant=self.request.tenant)


class InventoryViewSet(viewsets.ModelViewSet):
    """库存视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = InventorySerializer
    filterset_fields = ['warehouse', 'sku']
    
    def get_queryset(self):
        return Inventory.objects.filter(tenant=self.request.tenant).select_related('sku', 'sku__product', 'warehouse')
