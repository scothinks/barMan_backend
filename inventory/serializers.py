from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'cost', 'quantity', 'low_inventory_threshold']

class InventoryItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['quantity', 'low_inventory_threshold']