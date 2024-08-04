from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

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
        logger.info(f"Soft deleting item {self.id} - {self.name}")
        self.is_deleted = True
        self.delete_requested_at = timezone.now()
        self.save()
        logger.info(f"Item {self.id} - {self.name} soft deleted successfully")

    def restore(self):
        logger.info(f"Restoring item {self.id} - {self.name}")
        self.is_deleted = False
        self.delete_requested_at = None
        self.save()
        logger.info(f"Item {self.id} - {self.name} restored successfully")