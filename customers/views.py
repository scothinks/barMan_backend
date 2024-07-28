from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from .models import Customer, CustomerTab
from .serializers import CustomerSerializer, CustomerTabSerializer
from .permissions import CanCreateCustomers, CanCreateTabs, CanUpdateTabs
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [CanCreateCustomers]
        else:
            permission_classes = [permissions.IsAuthenticated]
        logger.info(f"Action: {self.action}, Permission classes: {[p.__name__ for p in permission_classes]}")
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        logger.info(f"Attempting to create customer with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
            logger.info(f"Customer created successfully: {serializer.data}")
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.exception(f"Error creating customer: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        logger.info("Retrieving customer list")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving customer details for ID: {kwargs.get('pk')}")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating customer with ID: {kwargs.get('pk')}, data: {request.data}")
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting customer with ID: {kwargs.get('pk')}")
        return super().destroy(request, *args, **kwargs)

class CustomerTabViewSet(viewsets.ModelViewSet):
    queryset = CustomerTab.objects.all()
    serializer_class = CustomerTabSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [CanCreateTabs]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [CanUpdateTabs]
        else:
            permission_classes = [permissions.IsAuthenticated]
        logger.info(f"Action: {self.action}, Permission classes: {[p.__name__ for p in permission_classes]}")
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        logger.info(f"Attempting to create customer tab with data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
            logger.info(f"Customer tab created successfully: {serializer.data}")
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            logger.exception(f"Error creating customer tab: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        logger.info("Retrieving customer tab list")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving customer tab details for ID: {kwargs.get('pk')}")
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        new_amount = serializer.validated_data.get('amount', instance.amount)
        if new_amount > instance.customer.tab_limit:
            return Response({"error": "Tab limit exceeded"}, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)
        return Response(serializer.data)


    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting customer tab with ID: {kwargs.get('pk')}")
        return super().destroy(request, *args, **kwargs)
    
class BatchCustomerOperations(APIView):
    def post(self, request):
        logger.info(f"Received batch operation request: {request.data}")
        operations = request.data
        results = {}

        for operation in operations:
            op_type = operation.get('operation')
            op_data = operation.get('data')
            logger.info(f"Processing operation: {op_type}")

            if op_type == 'getCustomers':
                customers = Customer.objects.all()
                results['customers'] = CustomerSerializer(customers, many=True).data
            elif op_type == 'getCustomerTabs':
                tabs = CustomerTab.objects.all()
                results['customerTabs'] = CustomerTabSerializer(tabs, many=True).data
            elif op_type == 'createCustomer':
                serializer = CustomerSerializer(data=op_data)
                if serializer.is_valid():
                    customer = serializer.save()
                    results['createdCustomer'] = CustomerSerializer(customer).data
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            elif op_type == 'createCustomerTab':
                serializer = CustomerTabSerializer(data=op_data)
                if serializer.is_valid():
                    tab = serializer.save()
                    results['createdTab'] = CustomerTabSerializer(tab).data
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": f"Unknown operation: {op_type}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(results)

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        logger.info(f"Batch operation permissions: {[p.__name__ for p in permission_classes]}")
        return [permission() for permission in permission_classes]
        pass