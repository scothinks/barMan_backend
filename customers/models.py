from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class CustomerTab(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sale = models.ForeignKey('sales.Sale', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer.name} - ₦{self.amount}"