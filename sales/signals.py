from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Sale

@receiver(post_save, sender=Sale)
def update_inventory_on_sale(sender, instance, created, **kwargs):
    inventory_item = instance.item
    if created:
        inventory_item.quantity -= instance.quantity
    else:
        original = Sale.objects.get(pk=instance.pk)
        quantity_difference = instance.quantity - original.quantity
        inventory_item.quantity -= quantity_difference
    
    inventory_item.save()

@receiver(post_delete, sender=Sale)
def update_inventory_on_sale_delete(sender, instance, **kwargs):
    inventory_item = instance.item
    inventory_item.quantity += instance.quantity
    inventory_item.save()