from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InventoryItemViewSet

router = DefaultRouter()
router.register(r'inventoryitems', InventoryItemViewSet, basename='inventoryitem')

urlpatterns = [
    path('', include(router.urls)),
]