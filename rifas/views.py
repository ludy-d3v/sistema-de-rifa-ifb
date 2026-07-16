from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from usuarios.permissions import IsOrganizador

from .models import Premio, Rifa, Transacao
from .serializers import (
    ComprovanteTransacaoSerializer,
    ImagemRifaSerializer,
    PremioSerializer,
    ReservaFormularioSerializer,
    ReservaSerializer,
    RifaPublicaSerializer,
    RifaSerializer,
    TransacaoSerializer,
)


class RifaViewSet(viewsets.ModelViewSet):
    serializer_class = RifaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizador]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return (
            Rifa.objects.filter(organizador=self.request.user)
            .prefetch_related('numeros', 'premios', 'imagens_galeria')
        )

    def perform_create(self, serializer):
        serializer.save(organizador=self.request.user)

    def perform_destroy(self, instance):
        try:
            instance.soft_delete()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message)

    @action(detail=True, methods=['post'], url_path='galeria')
    def adicionar_imagem_galeria(self, request, pk=None):
        rifa = self.get_object()
        if rifa.imagens_galeria.count() >= 5:
            raise ValidationError({'imagem': 'A galeria aceita no maximo 5 imagens.'})

        serializer = ImagemRifaSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(rifa=rifa)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PremioViewSet(viewsets.ModelViewSet):
    serializer_class = PremioSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizador]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_rifa(self):
        rifa = Rifa.objects.filter(pk=self.kwargs['rifa_pk'], organizador=self.request.user).first()
        if not rifa:
            raise PermissionDenied('Rifa nao encontrada para este organizador.')
        return rifa

    def get_queryset(self):
        return Premio.objects.filter(rifa=self.get_rifa())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['rifa'] = self.get_rifa()
        return context

    def perform_create(self, serializer):
        rifa = self.get_rifa()
        if rifa.premios.count() >= 5:
            raise ValidationError({'premios': 'A rifa aceita no maximo 5 premios.'})
        serializer.save(rifa=rifa)


class RifaPublicaAPIView(generics.RetrieveAPIView):
    serializer_class = RifaPublicaSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return (
            Rifa.objects.filter(ativo=True, status__in=[Rifa.Status.ATIVA, Rifa.Status.ENCERRADA])
            .prefetch_related('numeros', 'premios', 'imagens_galeria')
        )


class RifaPublicaListAPIView(generics.ListAPIView):
    serializer_class = RifaPublicaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Rifa.objects.filter(ativo=True, status=Rifa.Status.ATIVA)
            .prefetch_related('numeros', 'premios', 'imagens_galeria')
        )


class ReservarNumerosAPIView(generics.CreateAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        renderer = getattr(self.request, 'accepted_renderer', None)
        if getattr(renderer, 'format', None) in ['api', 'html']:
            return ReservaFormularioSerializer
        return super().get_serializer_class()

    def get_rifa(self):
        return get_object_or_404(Rifa, pk=self.kwargs['pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        rifa = self.get_rifa()
        context['rifa'] = rifa
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        transacao = serializer.save()
        return Response(
            TransacaoSerializer(transacao, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ReservarNumerosPorSlugAPIView(ReservarNumerosAPIView):
    def get_rifa(self):
        return get_object_or_404(Rifa, slug=self.kwargs['slug'])


class EnviarComprovanteAPIView(generics.UpdateAPIView):
    serializer_class = ComprovanteTransacaoSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    http_method_names = ['post', 'head', 'options']

    def get_queryset(self):
        return Transacao.objects.filter(status=Transacao.Status.RESERVADA)

    def post(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
