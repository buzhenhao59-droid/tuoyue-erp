from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """交易流水序列化器"""
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_no', 'biz_type', 'type', 'amount', 
                  'currency', 'description', 'status', 'created_at']
