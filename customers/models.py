from django.db import models
from django.db.models import Sum

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class CustomerTab(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tabs')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - ₦{self.amount}"

    @classmethod
    def update_tab_amount(cls, customer):
        from sales.models import Sale  # Import here to avoid circular import
        total_pending = Sale.objects.filter(
            customer=customer,
            payment_status='PENDING'
        ).aggregate(total=Sum('item__cost'))['total'] or 0

        tab, created = cls.objects.get_or_create(customer=customer)
        tab.amount = total_pending
        tab.save()

        # Remove any extra tabs for this customer
        cls.objects.filter(customer=customer).exclude(pk=tab.pk).delete()