import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import InventoryItem
from .serializers import InventoryItemSerializer, InventoryItemUpdateSerializer
from .permissions import CanUpdateInventory
from rest_framework.authentication import TokenAuthentication
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class InventoryItemViewSet(viewsets.ModelViewSet):
    throttle_classes = [UserRateThrottle]
    throttle_scope = 'inventory'
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name', 'cost']
    search_fields = ['name']
    ordering_fields = ['name', 'cost', 'quantity']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [CanUpdateInventory()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        item = self.get_object()
        serializer = InventoryItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if item.quantity <= item.low_inventory_threshold:
                # Send notification logic here
                print(f"Low inventory alert for item: {item.name}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
       try:
        logger.info(f"Listing inventory items for user: {request.user}")
        response = super().list(request, *args, **kwargs)
        logger.debug(f"Response data: {response.data}")
        return response
       except Exception as e:
        logger.error(f"Error in list method: {str(e)}", exc_info=True)
        return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        logger.info(f"Retrieving single inventory item for user: {request.user}")
        response = super().retrieve(request, *args, **kwargs)
        logger.debug(f"Response data: {response.data}")
        return response

    def create(self, request, *args, **kwargs):
        logger.info(f"Creating new inventory item for user: {request.user}")
        logger.debug(f"Request data: {request.data}")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        logger.info(f"Updating inventory item for user: {request.user}")
        logger.debug(f"Request data: {request.data}")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        logger.info(f"Deleting inventory item for user: {request.user}")
        return super().destroy(request, *args, **kwargs)