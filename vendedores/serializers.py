from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils.crypto import get_random_string
from rest_framework import serializers

from rifas.models import Rifa
from rifas.serializers import RifaSerializer

from .models import Vendedor, VendedorRifa


Usuario = get_user_model()


class VendedorRifaSerializer(serializers.ModelSerializer):
    rifa_titulo = serializers.CharField(source='rifa.titulo', read_only=True)

    class Meta:
        model = VendedorRifa
        fields = ['id', 'rifa', 'rifa_titulo', 'ativo', 'criado_em']
        read_only_fields = ['id', 'rifa_titulo', 'criado_em']


class VendedorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)
    rifas_associadas = VendedorRifaSerializer(many=True, read_only=True)

    class Meta:
        model = Vendedor
        fields = [
            'id',
            'nome',
            'email',
            'telefone',
            'comissao_fixa',
            'ativo',
            'rifas_associadas',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'nome', 'email', 'telefone', 'rifas_associadas', 'criado_em', 'atualizado_em']

    def validate_comissao_fixa(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError('A comissao fixa nao pode ser negativa.')
        return value


class CriarVendedorSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    comissao_fixa = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_email(self, value):
        if Usuario.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Ja existe usuario cadastrado com este e-mail.')
        return value

    def validate_comissao_fixa(self, value):
        if value < Decimal('0.00'):
            raise serializers.ValidationError('A comissao fixa nao pode ser negativa.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        organizador = self.context['request'].user
        senha_temporaria = get_random_string(12)
        usuario = Usuario.objects.create_user(
            email=validated_data['email'],
            password=senha_temporaria,
            nome=validated_data['nome'],
            telefone=validated_data.get('telefone', ''),
            papel=Usuario.Papel.VENDEDOR,
        )
        vendedor = Vendedor.objects.create(
            usuario=usuario,
            organizador=organizador,
            comissao_fixa=validated_data['comissao_fixa'],
        )
        send_mail(
            subject='Credenciais de acesso - RifaFacil',
            message=(
                f'Ola, {usuario.nome}.\n\n'
                'Seu acesso de vendedor foi criado.\n'
                f'E-mail: {usuario.email}\n'
                f'Senha temporaria: {senha_temporaria}\n\n'
                'Recomendamos alterar a senha no primeiro acesso.'
            ),
            from_email='nao-responda@rifafacil.local',
            recipient_list=[usuario.email],
            fail_silently=True,
        )
        vendedor.senha_temporaria = senha_temporaria
        return vendedor

    def to_representation(self, instance):
        data = VendedorSerializer(instance, context=self.context).data
        data['credenciais_enviadas'] = True
        data['senha_temporaria'] = getattr(instance, 'senha_temporaria', None)
        return data


class AssociarRifaSerializer(serializers.Serializer):
    rifa_id = serializers.IntegerField()

    def validate_rifa_id(self, value):
        organizador = self.context['request'].user
        rifa = Rifa.objects.filter(pk=value, organizador=organizador).first()
        if not rifa:
            raise serializers.ValidationError('Rifa nao encontrada para este organizador.')
        self.rifa = rifa
        return value

    def save(self, vendedor):
        associacao, _ = VendedorRifa.objects.update_or_create(
            vendedor=vendedor,
            rifa=self.rifa,
            defaults={'ativo': True},
        )
        return associacao


class RemoverRifaSerializer(serializers.Serializer):
    rifa_id = serializers.IntegerField()

    def validate_rifa_id(self, value):
        vendedor = self.context['vendedor']
        associacao = VendedorRifa.objects.filter(vendedor=vendedor, rifa_id=value).first()
        if not associacao:
            raise serializers.ValidationError('Associacao nao encontrada.')
        self.associacao = associacao
        return value

    def save(self):
        self.associacao.ativo = False
        self.associacao.save(update_fields=['ativo', 'atualizado_em'])
        return self.associacao


class VendedorRifaDashboardSerializer(serializers.ModelSerializer):
    rifa = RifaSerializer(read_only=True)

    class Meta:
        model = VendedorRifa
        fields = ['id', 'rifa', 'ativo', 'criado_em']


class VendedorResumoSerializer(serializers.Serializer):
    total_numeros_vendidos = serializers.IntegerField()
    total_numeros_pendentes = serializers.IntegerField()
    valor_bruto_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    comissao_estimada = serializers.DecimalField(max_digits=10, decimal_places=2)
    vendas = serializers.DictField()
