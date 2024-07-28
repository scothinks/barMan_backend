from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet

router = DefaultRouter()
router.register(r'inventoryitems', InventoryItemViewSet, basename='inventoryitem')

urlpatterns = [
    path('', include(router.urls)),
    path('inventoryitems/<int:pk>/soft-delete/', InventoryItemViewSet.as_view({'post': 'soft_delete'}), name='inventoryitem-soft-delete'),
    path('inventoryitems/<int:pk>/confirm-delete/', InventoryItemViewSet.as_view({'post': 'confirm_delete'}), name='inventoryitem-confirm-delete'),
    path('inventoryitems/<int:pk>/restore/', InventoryItemViewSet.as_view({'post': 'restore'}), name='inventoryitem-restore'),
    
]