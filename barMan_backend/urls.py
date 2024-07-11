from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from users.views import CustomAuthToken, CurrentUserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('inventory.urls')),
    path('api/token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
    path('api/sales/', include('sales.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/users/', include('users.urls')),
    path('api/users/me/', CurrentUserView.as_view(), name='current_user'),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]