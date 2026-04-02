from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """交易流水视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer
    filterset_fields = ['biz_type', 'type', 'status']
    
    def get_queryset(self):
        return Transaction.objects.filter(tenant=self.request.tenant)
