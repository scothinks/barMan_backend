from django.contrib import admin
from django.urls import path, include
from users.views import CustomAuthToken 

urlpatterns = [
    path('admin/inventoryItem', admin.site.urls),
    path('api/', include('inventory.urls')),
    path('api/token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/sales/', include('sales.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/users/', include('users.urls')),
    path('api-auth/', include('rest_framework.urls')),
]