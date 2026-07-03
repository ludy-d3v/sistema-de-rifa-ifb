from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PremioViewSet,
    ReservarNumerosAPIView,
    ReservarNumerosPorSlugAPIView,
    RifaPublicaAPIView,
    RifaViewSet,
)


router = DefaultRouter()
router.register('rifas', RifaViewSet, basename='rifa')

premio_list = PremioViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
premio_detail = PremioViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('', include(router.urls)),
    path('rifa/<slug:slug>/public/', RifaPublicaAPIView.as_view(), name='rifa-publica'),
    path('rifa/<int:pk>/reservar/', ReservarNumerosAPIView.as_view(), name='rifa-reservar'),
    path('rifa/<slug:slug>/reservar/', ReservarNumerosPorSlugAPIView.as_view(), name='rifa-reservar-slug'),
    path('rifas/<int:rifa_pk>/premios/', premio_list, name='premio-list'),
    path('rifas/<int:rifa_pk>/premios/<int:pk>/', premio_detail, name='premio-detail'),
]
