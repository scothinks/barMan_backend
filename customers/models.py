from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator
from decimal import Decimal

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    tab_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])

    def __str__(self):
        return self.name

class CustomerTab(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='tab')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
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
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        tab, created = cls.objects.get_or_create(customer=customer)
        tab.amount = total_pending
        tab.save()

        # Remove any extra tabs for this customer
        cls.objects.filter(customer=customer).exclude(pk=tab.pk).delete()
