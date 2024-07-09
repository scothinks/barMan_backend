from rest_framework import serializers
from .models import Sale
from inventory.models import InventoryItem
from customers.models import Customer

class SaleSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'item', 'item_name', 'quantity', 'timestamp', 'payment_status', 'customer', 'customer_name', 'recorded_by']
        read_only_fields = ['recorded_by', 'timestamp']

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        if item.quantity < quantity:
            raise serializers.ValidationError("Not enough inventory")
        item.quantity -= quantity
        item.save()
        return Sale.objects.create(**validated_data)