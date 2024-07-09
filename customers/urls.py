from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerTabViewSet

router = DefaultRouter()
router.register(r'tabs', CustomerTabViewSet, basename='customertab')
router.register(r'', CustomerViewSet, basename='customer')

urlpatterns = [
    path('', include(router.urls)),
]