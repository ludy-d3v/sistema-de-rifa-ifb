from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    VendedorResumoAPIView,
    VendedorRifasAPIView,
    VendedorVendasAPIView,
    VendedorViewSet,
)


router = DefaultRouter()
router.register('vendedores', VendedorViewSet, basename='vendedor')


urlpatterns = [
    path('', include(router.urls)),
    path('vendedor/rifas/', VendedorRifasAPIView.as_view(), name='vendedor-rifas'),
    path('vendedor/vendas/', VendedorVendasAPIView.as_view(), name='vendedor-vendas'),
    path('vendedor/resumo/', VendedorResumoAPIView.as_view(), name='vendedor-resumo'),
]
