from django.db import models
from django.contrib.auth import get_user_model
from inventory.models import InventoryItem

class Sale(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=10, choices=[('DONE', 'Done'), ('PENDING', 'Pending')])
    recorded_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"