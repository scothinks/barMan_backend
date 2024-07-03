from rest_framework import serializers
from .models import Customer, CustomerTab

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone_number']

class CustomerTabSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)

    class Meta:
        model = CustomerTab
        fields = ['id', 'customer', 'customer_name', 'sale', 'amount']