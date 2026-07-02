from decimal import Decimal

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.permissions import IsOrganizador, IsVendedor

from .models import Vendedor, VendedorRifa
from .serializers import (
    AssociarRifaSerializer,
    CriarVendedorSerializer,
    RemoverRifaSerializer,
    VendedorResumoSerializer,
    VendedorRifaDashboardSerializer,
    VendedorRifaSerializer,
    VendedorSerializer,
)


class VendedorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizador]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return (
            Vendedor.objects.filter(organizador=self.request.user)
            .select_related('usuario', 'organizador')
            .prefetch_related('rifas_associadas__rifa')
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return CriarVendedorSerializer
        return VendedorSerializer

    @action(detail=True, methods=['post'], url_path='associar-rifa')
    def associar_rifa(self, request, pk=None):
        vendedor = self.get_object()
        serializer = AssociarRifaSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        associacao = serializer.save(vendedor=vendedor)
        return Response(
            VendedorRifaSerializer(associacao, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=['delete'], url_path='remover-rifa')
    def remover_rifa(self, request, pk=None):
        vendedor = self.get_object()
        serializer = RemoverRifaSerializer(
            data=request.data,
            context={'request': request, 'vendedor': vendedor},
        )
        serializer.is_valid(raise_exception=True)
        associacao = serializer.save()
        return Response(
            VendedorRifaSerializer(associacao, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


class VendedorBaseAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVendedor]

    def get_vendedor(self):
        vendedor = (
            Vendedor.objects.filter(usuario=self.request.user, ativo=True)
            .select_related('usuario', 'organizador')
            .first()
        )
        if not vendedor:
            raise PermissionDenied('Perfil de vendedor nao encontrado ou inativo.')
        return vendedor


class VendedorRifasAPIView(VendedorBaseAPIView):
    def get(self, request):
        vendedor = self.get_vendedor()
        associacoes = (
            VendedorRifa.objects.filter(vendedor=vendedor, ativo=True, rifa__ativo=True)
            .select_related('rifa', 'rifa__organizador')
            .prefetch_related('rifa__numeros', 'rifa__premios', 'rifa__imagens_galeria')
        )
        serializer = VendedorRifaDashboardSerializer(
            associacoes,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)


class VendedorVendasAPIView(VendedorBaseAPIView):
    def get(self, request):
        self.get_vendedor()
        return Response(
            {
                'resultados': [],
                'mensagem': 'As vendas serao listadas quando o modulo de transacoes for implementado.',
            }
        )


class VendedorResumoAPIView(VendedorBaseAPIView):
    def get(self, request):
        vendedor = self.get_vendedor()
        data = {
            'total_numeros_vendidos': 0,
            'total_numeros_pendentes': 0,
            'valor_bruto_total': Decimal('0.00'),
            'comissao_estimada': Decimal('0.00') * vendedor.comissao_fixa,
            'vendas': {
                'aprovadas': 0,
                'pendentes': 0,
                'rejeitadas': 0,
            },
        }
        serializer = VendedorResumoSerializer(data)
        return Response(serializer.data)
