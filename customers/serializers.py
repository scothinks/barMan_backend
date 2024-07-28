from rest_framework import serializers
from .models import Customer, CustomerTab

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number', 'tab_limit']

class CustomerTabSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_id = serializers.IntegerField(source='customer.id', read_only=True)
    tab_limit = serializers.DecimalField(source='customer.tab_limit', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CustomerTab
        fields = ['id', 'customer', 'customer_id', 'customer_name', 'amount', 'tab_limit']