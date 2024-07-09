from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Sale
from .serializers import SaleSerializer
from customers.models import Customer, CustomerTab
from .permissions import IsSuperAdmin
from django.db import transaction

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        with transaction.atomic():
            sale = serializer.save(recorded_by=self.request.user)
            if sale.customer:
                CustomerTab.update_tab_amount(sale.customer)

    def perform_update(self, serializer):
        with transaction.atomic():
            old_customer = self.get_object().customer
            sale = serializer.save()
            if old_customer:
                CustomerTab.update_tab_amount(old_customer)
            if sale.customer:
                CustomerTab.update_tab_amount(sale.customer)

    @action(detail=True, methods=['patch'])
    def update_payment_status(self, request, pk=None):
        sale = self.get_object()
        status = request.data.get('payment_status')
        if status not in ['PENDING', 'DONE']:
            return Response({'error': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            sale.payment_status = status
            sale.save()
            if sale.customer:
                CustomerTab.update_tab_amount(sale.customer)
        
        return Response({'status': 'payment status updated'})

    @action(detail=True, methods=['post'])
    def allocate_to_customer(self, request, pk=None):
        sale = self.get_object()
        customer_id = request.data.get('customer_id')
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            old_customer = sale.customer
            sale.customer = customer
            sale.save()
            
            if old_customer:
                CustomerTab.update_tab_amount(old_customer)
            CustomerTab.update_tab_amount(customer)
        
        return Response({'status': 'sale allocated to customer'})