from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'can_update_inventory', 'can_report_sales', 'can_create_customers', 'can_create_tabs', 'can_update_tabs', 'can_manage_users']
        read_only_fields = ['id', 'email']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'can_update_inventory', 'can_report_sales', 'can_create_tabs', 'can_update_tabs']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user