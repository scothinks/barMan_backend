from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    can_update_inventory = models.BooleanField(default=False)
    can_report_sales = models.BooleanField(default=False)
    can_create_tabs = models.BooleanField(default=False)
    can_update_tabs = models.BooleanField(default=False)

    def __str__(self):
        return self.username