from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PremioViewSet, RifaViewSet


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
    path('rifas/<int:rifa_pk>/premios/', premio_list, name='premio-list'),
    path('rifas/<int:rifa_pk>/premios/<int:pk>/', premio_detail, name='premio-detail'),
]
