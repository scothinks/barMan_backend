import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Sale
from .serializers import SaleSerializer
from customers.models import Customer, CustomerTab
from .permissions import IsSuperAdmin
from django.db import transaction
from inventory.models import InventoryItem
from django.db.models import Sum, Q
from rest_framework.pagination import PageNumberPagination
from django.utils.dateparse import parse_date
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by('-timestamp')
    serializer_class = SaleSerializer
    permission_classes = [IsSuperAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payment_status', 'customer']

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
        status_value = request.data.get('payment_status')
        if status_value not in ['PENDING', 'DONE']:
            return Response({'error': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            sale.payment_status = status_value
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
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Received sale data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            customer = serializer.validated_data.get('customer')
            
            if customer:
                customer_tab, created = CustomerTab.objects.get_or_create(customer=customer)
                new_tab_amount = customer_tab.amount + serializer.validated_data['total_amount']
                
                if new_tab_amount > customer.tab_limit:
                    return Response({"error": "This sale would exceed the customer's tab limit"}, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"Sale created successfully: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.error(f"Error creating sale: {str(e)}")
            return Response({'error': 'Failed to create sale'}, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        logger.info("Fetching sales list")
        queryset = self.filter_queryset(self.get_queryset())
        
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        if start_date:
            start_date = parse_date(start_date)
            if start_date:
                queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            end_date = parse_date(end_date)
            if end_date:
                queryset = queryset.filter(timestamp__date__lte=end_date)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data).data
        else:
            serializer = self.get_serializer(queryset, many=True)
            paginated_data = {
                'results': serializer.data,
                'count': queryset.count(),
                'next': None,
                'previous': None,
            }

        total_done = queryset.filter(payment_status='DONE').aggregate(
            total=Sum('total_amount'))['total'] or 0
        total_pending = queryset.filter(payment_status='PENDING').aggregate(
            total=Sum('total_amount'))['total'] or 0

        response_data = {
            'sales': paginated_data['results'],
            'summary': {
                'total_done': float(total_done),
                'total_pending': float(total_pending)
            },
            'next': paginated_data.get('next'),
            'previous': paginated_data.get('previous'),
            'count': paginated_data.get('count')
        }
        logger.info(f"Returning sales data: {response_data}")
        return Response(response_data)

    @action(detail=False, methods=['GET'])
    def search(self, request):
        logger.info("Performing sales search")
        queryset = self.get_queryset()
        
        customer_name = request.query_params.get('customer')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        period = request.query_params.get('period')

        logger.info(f"Filters received: customer={customer_name}, start_date={start_date}, end_date={end_date}, period={period}")

        if customer_name:
            queryset = queryset.filter(Q(customer__name__icontains=customer_name) | Q(item__name__icontains=customer_name))

        if period:
            end_date = timezone.now()
            if period == 'day' or period == 'last 24 hours':
                start_date = end_date - timedelta(days=1)
            elif period == 'week':
                start_date = end_date - timedelta(days=7)
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
            elif period == 'year':
                start_date = end_date - timedelta(days=365)
            elif period == 'all':
                start_date = None
            else:
                return Response({"error": "Invalid period"}, status=status.HTTP_400_BAD_REQUEST)
            
            if start_date:
                queryset = queryset.filter(timestamp__range=[start_date, end_date])
        elif start_date or end_date:
            if start_date:
                start_date = parse_date(start_date)
                if start_date:
                    queryset = queryset.filter(timestamp__date__gte=start_date)
            if end_date:
                end_date = parse_date(end_date)
                if end_date:
                    queryset = queryset.filter(timestamp__date__lte=end_date)

        logger.info(f"Filtered queryset: {queryset.query}")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            result = Response(serializer.data)

        total_done = queryset.filter(payment_status='DONE').aggregate(
            total=Sum('total_amount'))['total'] or 0
        total_pending = queryset.filter(payment_status='PENDING').aggregate(
            total=Sum('total_amount'))['total'] or 0

        result.data['summary'] = {
            'total_done': float(total_done),
            'total_pending': float(total_pending)
        }

        logger.info(f"Returning search results: {result.data}")
        return result
