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
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

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
        logger.info(f"Getting permissions for action: {self.action}")
        logger.info(f"User: {self.request.user}, Authenticated: {self.request.user.is_authenticated}")
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'update_quantity']:
            logger.info("Applying CanUpdateInventory permission")
            return [CanUpdateInventory()]
        logger.info("Applying IsAuthenticated permission")
        return [permissions.IsAuthenticated()]

    def initial(self, request, *args, **kwargs):
        logger.info(f"Initial method called for action: {self.action}")
        logger.info(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
        logger.info(f"Request headers: {request.headers}")
        super().initial(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        item = self.get_object()
        serializer = InventoryItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if item.quantity <= item.low_inventory_threshold:
                # Send notification logic here
                logger.warning(f"Low inventory alert for item: {item.name}")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        try:
            logger.info(f"Listing inventory items for user: {request.user}")
            logger.info(f"User permissions: {request.user.get_all_permissions()}")
            response = super().list(request, *args, **kwargs)
            logger.debug(f"Response data: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error in list method: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        try:
            logger.info(f"Retrieving single inventory item for user: {request.user}")
            response = super().retrieve(request, *args, **kwargs)
            logger.debug(f"Response data: {response.data}")
            return response
        except Exception as e:
            logger.error(f"Error in retrieve method: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        try:
            logger.info(f"Creating new inventory item for user: {request.user}")
            logger.debug(f"Request data: {request.data}")
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                logger.info(f"Successfully created inventory item: {serializer.data}")
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            logger.warning(f"Invalid data for creating inventory item: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in create method: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            logger.info(f"Updating inventory item for user: {request.user}")
            logger.debug(f"Request data: {request.data}")
            return super().update(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in update method: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        try:
            logger.info(f"Deleting inventory item for user: {request.user}")
            return super().destroy(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in destroy method: {str(e)}", exc_info=True)
            return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_exception(self, exc):
        if isinstance(exc, AuthenticationFailed):
            logger.error(f"Authentication failed for user: {self.request.user}")
            return Response({"error": "Authentication failed"}, status=status.HTTP_401_UNAUTHORIZED)
        elif isinstance(exc, PermissionDenied):
            logger.error(f"Permission denied for user: {self.request.user}")
            return Response({"error": "You don't have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        return super().handle_exception(exc)