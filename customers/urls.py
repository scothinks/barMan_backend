from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerTabViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'tabs', CustomerTabViewSet)

urlpatterns = [
    path('', include(router.urls)),
]