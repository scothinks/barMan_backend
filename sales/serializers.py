from rest_framework import serializers
from .models import Sale
from inventory.models import InventoryItem

class SaleSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)

    class Meta:
        model = Sale
        fields = ['id', 'item', 'item_name', 'quantity', 'timestamp', 'payment_status', 'recorded_by']
        read_only_fields = ['recorded_by']

    def create(self, validated_data):
        item = validated_data['item']
        quantity = validated_data['quantity']
        if item.quantity < quantity:
            raise serializers.ValidationError("Not enough inventory")
        item.quantity -= quantity
        item.save()
        return Sale.objects.create(**validated_data)