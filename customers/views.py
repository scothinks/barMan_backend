from rest_framework import viewsets, permissions
from .models import Customer, CustomerTab
from .serializers import CustomerSerializer, CustomerTabSerializer
from .permissions import CanCreateTabs, CanUpdateTabs

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

class CustomerTabViewSet(viewsets.ModelViewSet):
    queryset = CustomerTab.objects.all()
    serializer_class = CustomerTabSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [CanCreateTabs]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [CanUpdateTabs]
        return super().get_permissions()