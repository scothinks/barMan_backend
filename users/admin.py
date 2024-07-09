from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_staff', 'can_update_inventory', 'can_report_sales', 'can_create_tabs', 'can_update_tabs', 'can_create_customers']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Permissions', {'fields': ('can_update_inventory', 'can_report_sales', 'can_create_tabs', 'can_update_tabs', 'can_create_customers')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)