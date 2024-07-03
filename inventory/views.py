from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import InventoryItem
from .serializers import InventoryItemSerializer, InventoryItemUpdateSerializer
from .permissions import CanUpdateInventory

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [CanUpdateInventory]
        return super().get_permissions()

    @action(detail=True, methods=['patch'])
    def update_quantity(self, request, pk=None):
        item = self.get_object()
        serializer = InventoryItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if item.quantity <= item.low_inventory_threshold:
                # Send notification logic here
                pass
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)