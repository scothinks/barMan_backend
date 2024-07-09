from django.db import models
from django.core.validators import MinValueValidator

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator('0.01')])
    quantity = models.IntegerField(default=0)
    low_inventory_threshold = models.IntegerField(default=10)

    def __str__(self):
        return self.name