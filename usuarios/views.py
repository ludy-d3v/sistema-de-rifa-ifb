from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CadastroSerializer,
    LoginSerializer,
    RecuperarSenhaSerializer,
    RedefinirSenhaSerializer,
    UsuarioSerializer,
)


class StatusAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                'status': 'online',
                'servico': 'RifaFacil API',
                'versao': '0.1.0',
            }
        )


class RootAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    name = 'Api Root'

    def get(self, request):
        base_url = request.build_absolute_uri('/api/')
        return Response(
            {
                'status': f'{base_url}status/',
                'documentacao': f'{base_url}docs/',
                'cadastro': f'{base_url}cadastro/',
                'login': f'{base_url}login/',
                'renovar_token': f'{base_url}renovar-token/',
                'recuperar_senha': f'{base_url}recuperar-senha/',
                'redefinir_senha': f'{base_url}redefinir-senha/<uid>/<token>/',
                'perfil': f'{base_url}perfil/',
                'rifas': f'{base_url}rifas/',
                'rifas_publicas': f'{base_url}rifas-publicas/',
                'rifa_publica': f'{base_url}rifa/<slug>/public/',
                'reservar_numeros': f'{base_url}rifa/<slug>/reservar/',
                'enviar_comprovante': f'{base_url}transacoes/<id>/comprovante/',
                'vendedores': f'{base_url}vendedores/',
                'vendedor_rifas': f'{base_url}vendedor/rifas/',
                'vendedor_vendas': f'{base_url}vendedor/vendas/',
                'vendedor_resumo': f'{base_url}vendedor/resumo/',
            }
        )


class CadastroAPIView(generics.CreateAPIView):
    serializer_class = CadastroSerializer
    permission_classes = [permissions.AllowAny]


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]


class PerfilAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_object(self):
        return self.request.user


class RecuperarSenhaAPIView(generics.GenericAPIView):
    serializer_class = RecuperarSenhaSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_200_OK)


class RedefinirSenhaAPIView(generics.GenericAPIView):
    serializer_class = RedefinirSenhaSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid, token):
        serializer = self.get_serializer(
            data=request.data,
            context={'uid': uid, 'token': token},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_200_OK)
