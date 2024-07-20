from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SaleViewSet
from rest_framework.documentation import include_docs_urls

router = DefaultRouter()
router.register(r'', SaleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', SaleViewSet.as_view({'get': 'search'}), name='sale-search'),
    path('docs/', include_docs_urls(title='Sales API')),
]
