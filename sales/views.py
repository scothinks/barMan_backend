from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Sale
from .serializers import SaleSerializer
from .permissions import CanReportSales

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [CanReportSales]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        pending_sum = Sale.objects.filter(payment_status='PENDING').count()
        done_sum = Sale.objects.filter(payment_status='DONE').count()
        return Response({
            'pending_transactions': pending_sum,
            'done_transactions': done_sum
        })