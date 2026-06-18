from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CadastroAPIView,
    LoginAPIView,
    PerfilAPIView,
    RecuperarSenhaAPIView,
    RedefinirSenhaAPIView,
)


urlpatterns = [
    path('cadastro/', CadastroAPIView.as_view(), name='cadastro'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('renovar-token/', TokenRefreshView.as_view(), name='renovar-token'),
    path('recuperar-senha/', RecuperarSenhaAPIView.as_view(), name='recuperar-senha'),
    path('redefinir-senha/', RedefinirSenhaAPIView.as_view(), name='redefinir-senha'),
    path('perfil/', PerfilAPIView.as_view(), name='perfil'),
]
