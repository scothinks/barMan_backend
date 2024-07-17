from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from users.views import CustomAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('inventory/', include('inventory.urls')),
        path('sales/', include('sales.urls')),
        path('customers/', include('customers.urls')),
        path('users/', include('users.urls')),
        path('token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    ])),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
