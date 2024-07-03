from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/inventory/', include('inventory.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/users/', include('users.urls')),
    path('api-auth/', include('rest_framework.urls')),
]