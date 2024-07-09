from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import InventoryItem
from customers.models import Customer, CustomerTab

class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DONE', 'Done'),
    ]
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.customer:
            CustomerTab.update_tab_amount(self.customer)