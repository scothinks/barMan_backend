from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantity = models.IntegerField(default=0)
    low_inventory_threshold = models.IntegerField(default=10)
    is_deleted = models.BooleanField(default=False)
    delete_requested_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name

    def soft_delete(self):
        self.is_deleted = True
        self.delete_requested_at = timezone.now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.delete_requested_at = None
        self.save()