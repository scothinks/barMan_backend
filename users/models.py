from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Inventory permissions
    can_update_inventory = models.BooleanField(default=False)
    
    # Sales permissions
    can_report_sales = models.BooleanField(default=False)
    
    # Customer permissions
    can_create_customers = models.BooleanField(default=False)
    
    # Tab permissions
    can_create_tabs = models.BooleanField(default=False)
    can_update_tabs = models.BooleanField(default=False)
    
    # User management permissions
    can_manage_users = models.BooleanField(default=False)

    def __str__(self):
        return self.username