from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from inventory.models import InventoryItem
from customers.models import Customer, CustomerTab
from decimal import Decimal

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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.item.name} - {self.quantity} units"

    def save(self, *args, **kwargs):
        # Always calculate total_amount, regardless of whether it's a new or existing sale
        self.total_amount = self.item.cost * self.quantity
        super().save(*args, **kwargs)

@receiver(post_save, sender=Sale)
def update_inventory_and_tab_on_sale(sender, instance, created, **kwargs):
    # Update inventory
    inventory_item = instance.item
    if created:
        inventory_item.quantity -= instance.quantity
    else:
        original = Sale.objects.get(pk=instance.pk)
        quantity_difference = instance.quantity - original.quantity
        inventory_item.quantity -= quantity_difference
    
    inventory_item.save()

    # Update customer tab
    if instance.customer:
        CustomerTab.update_tab_amount(instance.customer)

@receiver(post_delete, sender=Sale)
def update_inventory_and_tab_on_sale_delete(sender, instance, **kwargs):
    # Update inventory
    inventory_item = instance.item
    inventory_item.quantity += instance.quantity
    inventory_item.save()

    # Update customer tab
    if instance.customer:
        CustomerTab.update_tab_amount(instance.customer)