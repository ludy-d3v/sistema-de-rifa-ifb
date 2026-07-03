from decimal import Decimal

from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from rifas.models import Transacao
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
        if self.action == 'associar_rifa':
            return AssociarRifaSerializer
        if self.action == 'remover_rifa':
            return RemoverRifaSerializer
        return VendedorSerializer

    @extend_schema(
        request=AssociarRifaSerializer,
        responses=VendedorRifaSerializer,
        description='Associa um vendedor ja cadastrado a uma rifa do organizador autenticado.',
    )
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

    @extend_schema(
        request=RemoverRifaSerializer,
        responses=VendedorRifaSerializer,
        description='Desativa a associacao entre vendedor e rifa.',
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
        vendedor = self.get_vendedor()
        transacoes = (
            Transacao.objects.filter(vendedor=vendedor)
            .select_related('rifa')
            .prefetch_related('itens__numero')
            .order_by('-criado_em')
        )
        resultados = []
        for transacao in transacoes:
            resultados.append(
                {
                    'id': transacao.id,
                    'data': transacao.criado_em,
                    'rifa': transacao.rifa.titulo,
                    'comprador': transacao.comprador_nome,
                    'numeros': [item.numero.numero for item in transacao.itens.all()],
                    'status': transacao.status,
                    'valor_total': transacao.valor_total,
                }
            )
        return Response(
            {
                'resultados': resultados,
            }
        )


class VendedorResumoAPIView(VendedorBaseAPIView):
    def get(self, request):
        vendedor = self.get_vendedor()
        transacoes = Transacao.objects.filter(vendedor=vendedor)
        aprovadas = transacoes.filter(status=Transacao.Status.PAGA)
        pendentes = transacoes.filter(status__in=[Transacao.Status.RESERVADA, Transacao.Status.AGUARDANDO_APROVACAO])
        rejeitadas = transacoes.filter(status__in=[Transacao.Status.REJEITADA, Transacao.Status.EXPIRADA])
        total_numeros_vendidos = sum(transacao.itens.count() for transacao in aprovadas)
        total_numeros_pendentes = sum(transacao.itens.count() for transacao in pendentes)
        valor_bruto_total = sum((transacao.valor_total for transacao in transacoes), Decimal('0.00'))
        comissao_estimada = vendedor.comissao_fixa * total_numeros_vendidos
        data = {
            'total_numeros_vendidos': total_numeros_vendidos,
            'total_numeros_pendentes': total_numeros_pendentes,
            'valor_bruto_total': valor_bruto_total,
            'comissao_estimada': comissao_estimada,
            'vendas': {
                'aprovadas': aprovadas.count(),
                'pendentes': pendentes.count(),
                'rejeitadas': rejeitadas.count(),
            },
        }
        serializer = VendedorResumoSerializer(data)
        return Response(serializer.data)
