from rest_framework import serializers
from .models import Sale
from inventory.models import InventoryItem
from customers.models import Customer

class SaleSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    recorded_by_username = serializers.CharField(source='recorded_by.username', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'item', 'item_name', 'quantity', 'timestamp', 'payment_status', 'customer', 'customer_name', 'recorded_by', 'recorded_by_username', 'total_amount']
        read_only_fields = ['recorded_by', 'timestamp', 'total_amount']

    def validate(self, data):
        item = data['item']
        quantity = data['quantity']
        if item.quantity < quantity:
            raise serializers.ValidationError("Not enough inventory")
        return data

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        total_amount = item.cost * quantity
        validated_data['total_amount'] = total_amount
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_amount'] = float(representation['total_amount'])
        return representation