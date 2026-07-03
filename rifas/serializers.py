from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from vendedores.models import Vendedor

from .models import ImagemRifa, ItemTransacao, NumeroRifa, Premio, Rifa, Transacao


class NumeroRifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumeroRifa
        fields = ['id', 'numero', 'status']
        read_only_fields = ['id', 'numero', 'status']


class ImagemRifaSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = ImagemRifa
        fields = ['id', 'imagem', 'imagem_url', 'ordem', 'criado_em']
        read_only_fields = ['id', 'imagem_url', 'criado_em']

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if not obj.imagem:
            return ''
        url = obj.imagem.url
        return request.build_absolute_uri(url) if request else url


class PremioSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = Premio
        fields = ['id', 'rifa', 'posicao', 'descricao', 'imagem', 'imagem_url', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'rifa', 'imagem_url', 'criado_em', 'atualizado_em']

    def validate_posicao(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('A posicao do premio deve estar entre 1 e 5.')
        return value

    def validate(self, attrs):
        rifa = self.context.get('rifa') or getattr(self.instance, 'rifa', None)
        posicao = attrs.get('posicao', getattr(self.instance, 'posicao', None))

        if rifa and posicao:
            premios = Premio.objects.filter(rifa=rifa, posicao=posicao)
            if self.instance:
                premios = premios.exclude(pk=self.instance.pk)
            if premios.exists():
                raise serializers.ValidationError({'posicao': 'Ja existe premio nesta posicao.'})
        return attrs

    def get_imagem_url(self, obj):
        request = self.context.get('request')
        if not obj.imagem:
            return ''
        url = obj.imagem.url
        return request.build_absolute_uri(url) if request else url


class RifaSerializer(serializers.ModelSerializer):
    organizador = serializers.StringRelatedField(read_only=True)
    numeros = NumeroRifaSerializer(many=True, read_only=True)
    premios = PremioSerializer(many=True, read_only=True)
    imagens_galeria = ImagemRifaSerializer(many=True, read_only=True)
    imagens_galeria_upload = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    quantidade_numeros = serializers.IntegerField(source='numeros.count', read_only=True)
    quantidade_premios = serializers.IntegerField(source='premios.count', read_only=True)

    class Meta:
        model = Rifa
        fields = [
            'id',
            'titulo',
            'slug',
            'descricao',
            'descricao_html',
            'valor_numero',
            'total_numeros',
            'data_sorteio',
            'chave_pix',
            'tempo_reserva',
            'status',
            'organizador',
            'imagem_principal',
            'imagens_galeria',
            'imagens_galeria_upload',
            'link_transmissao',
            'ativo',
            'excluido_em',
            'quantidade_numeros',
            'quantidade_premios',
            'numeros',
            'premios',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = [
            'id',
            'slug',
            'organizador',
            'ativo',
            'excluido_em',
            'quantidade_numeros',
            'quantidade_premios',
            'numeros',
            'premios',
            'imagens_galeria',
            'criado_em',
            'atualizado_em',
        ]

    def validate_total_numeros(self, value):
        if value < 1:
            raise serializers.ValidationError('A rifa precisa ter pelo menos 1 numero.')
        if value > 10000:
            raise serializers.ValidationError('O limite inicial e de 10000 numeros por rifa.')
        return value

    def validate_tempo_reserva(self, value):
        if value < 1:
            raise serializers.ValidationError('O tempo de reserva deve ser de pelo menos 1 minuto.')
        return value

    def validate_imagens_galeria_upload(self, value):
        if len(value) > 5:
            raise serializers.ValidationError('A galeria aceita no maximo 5 imagens.')
        return value

    def validate(self, attrs):
        if self.instance and self.instance.possui_vendas:
            campos_bloqueados = ['valor_numero', 'total_numeros']
            erros = {}
            for campo in campos_bloqueados:
                if campo in attrs and attrs[campo] != getattr(self.instance, campo):
                    erros[campo] = 'Este campo nao pode ser alterado apos a primeira venda.'
            if erros:
                raise serializers.ValidationError(erros)
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        imagens = validated_data.pop('imagens_galeria_upload', [])
        rifa = Rifa.objects.create(**validated_data)
        NumeroRifa.objects.bulk_create(
            NumeroRifa(rifa=rifa, numero=numero)
            for numero in range(1, rifa.total_numeros + 1)
        )
        self._salvar_galeria(rifa, imagens)
        return rifa

    @transaction.atomic
    def update(self, instance, validated_data):
        imagens = validated_data.pop('imagens_galeria_upload', None)
        rifa = super().update(instance, validated_data)
        if imagens is not None:
            rifa.imagens_galeria.all().delete()
            self._salvar_galeria(rifa, imagens)
        return rifa

    def _salvar_galeria(self, rifa, imagens):
        ImagemRifa.objects.bulk_create(
            ImagemRifa(rifa=rifa, imagem=imagem, ordem=indice)
            for indice, imagem in enumerate(imagens, start=1)
        )


class VendedorPublicoSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome', read_only=True)

    class Meta:
        model = Vendedor
        fields = ['id', 'nome']


class RifaPublicaSerializer(serializers.ModelSerializer):
    imagem_principal_url = serializers.SerializerMethodField()
    imagens_galeria = ImagemRifaSerializer(many=True, read_only=True)
    premios = PremioSerializer(many=True, read_only=True)
    numeros = NumeroRifaSerializer(many=True, read_only=True)
    vendedores = serializers.SerializerMethodField()
    total_numeros = serializers.IntegerField(read_only=True)
    numeros_pagos = serializers.SerializerMethodField()
    percentual_vendido = serializers.SerializerMethodField()

    class Meta:
        model = Rifa
        fields = [
            'id',
            'slug',
            'titulo',
            'descricao',
            'descricao_html',
            'valor_numero',
            'total_numeros',
            'data_sorteio',
            'status',
            'imagem_principal',
            'imagem_principal_url',
            'imagens_galeria',
            'premios',
            'numeros',
            'vendedores',
            'link_transmissao',
            'numeros_pagos',
            'percentual_vendido',
        ]

    def get_imagem_principal_url(self, obj):
        request = self.context.get('request')
        if not obj.imagem_principal:
            return ''
        url = obj.imagem_principal.url
        return request.build_absolute_uri(url) if request else url

    def get_vendedores(self, obj):
        vendedores = Vendedor.objects.filter(
            rifas_associadas__rifa=obj,
            rifas_associadas__ativo=True,
            ativo=True,
            usuario__is_active=True,
        ).select_related('usuario').distinct()
        return VendedorPublicoSerializer(vendedores, many=True).data

    def get_numeros_pagos(self, obj):
        return obj.numeros.filter(status=NumeroRifa.Status.PAGO).count()

    def get_percentual_vendido(self, obj):
        if not obj.total_numeros:
            return 0
        return round((self.get_numeros_pagos(obj) / obj.total_numeros) * 100, 2)


class ReservaSerializer(serializers.Serializer):
    numeros = serializers.ListField(
        label='Numeros',
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=False,
        help_text='Use este campo em JSON. Exemplo: [1, 2, 3].',
    )
    numeros_texto = serializers.CharField(
        label='Numeros selecionados',
        required=False,
        allow_blank=True,
        write_only=True,
        help_text='Informe os numeros separados por virgula. Exemplo: 1,2,3.',
    )
    comprador_nome = serializers.CharField(label='Nome do comprador', max_length=150)
    comprador_email = serializers.EmailField(label='E-mail do comprador')
    comprador_telefone = serializers.CharField(label='Telefone do comprador', max_length=20)
    comprador_cpf = serializers.CharField(label='CPF do comprador', max_length=14)
    vendedor = serializers.ChoiceField(
        label='Vendedor',
        choices=[],
        required=False,
        write_only=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rifa = self.context.get('rifa')
        if rifa:
            vendedores = Vendedor.objects.filter(
                rifas_associadas__rifa=rifa,
                rifas_associadas__ativo=True,
                ativo=True,
                usuario__is_active=True,
            ).select_related('usuario').distinct()
            self.fields['vendedor'].choices = [
                (str(vendedor.id), vendedor.usuario.nome)
                for vendedor in vendedores
            ]
            self.fields['vendedor'].required = vendedores.exists()

    def to_internal_value(self, data):
        if 'vendedor' not in data and 'vendedor_id' in data:
            data = data.copy()
            data['vendedor'] = data.get('vendedor_id')
        return super().to_internal_value(data)

    def validate_numeros(self, value):
        numeros_unicos = list(dict.fromkeys(value))
        if len(numeros_unicos) != len(value):
            raise serializers.ValidationError('Nao envie numeros repetidos na mesma reserva.')
        return numeros_unicos

    def validate(self, attrs):
        rifa = self.context['rifa']
        if not rifa.ativo or rifa.status != Rifa.Status.ATIVA:
            raise serializers.ValidationError('Esta rifa nao esta disponivel para reservas.')

        numeros_texto = attrs.pop('numeros_texto', '')
        if 'numeros' not in attrs and numeros_texto:
            try:
                attrs['numeros'] = [
                    int(numero.strip())
                    for numero in numeros_texto.replace(';', ',').split(',')
                    if numero.strip()
                ]
            except ValueError:
                raise serializers.ValidationError({'numeros_texto': 'Informe apenas numeros separados por virgula.'})
            attrs['numeros'] = self.validate_numeros(attrs['numeros'])

        if 'numeros' not in attrs:
            raise serializers.ValidationError({'numeros': 'Informe os numeros em JSON ou use numeros_texto no formulario HTML.'})

        vendedor_id = attrs.get('vendedor')
        if vendedor_id:
            vendedor_id = int(vendedor_id)
            vendedor = Vendedor.objects.filter(
                pk=vendedor_id,
                ativo=True,
                usuario__is_active=True,
                rifas_associadas__rifa=rifa,
                rifas_associadas__ativo=True,
            ).first()
            if not vendedor:
                raise serializers.ValidationError({'vendedor': 'Vendedor nao associado a esta rifa.'})
            attrs['vendedor'] = vendedor
        else:
            attrs['vendedor'] = None
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        rifa = self.context['rifa']
        numeros_solicitados = validated_data.pop('numeros')
        vendedor = validated_data.pop('vendedor', None)

        numeros = list(
            NumeroRifa.objects.select_for_update().filter(
                rifa=rifa,
                numero__in=numeros_solicitados,
            )
        )
        encontrados = {numero.numero for numero in numeros}
        faltantes = sorted(set(numeros_solicitados) - encontrados)
        if faltantes:
            raise serializers.ValidationError({'numeros': f'Numeros inexistentes nesta rifa: {faltantes}.'})

        indisponiveis = [
            numero.numero
            for numero in numeros
            if numero.status != NumeroRifa.Status.DISPONIVEL
        ]
        if indisponiveis:
            raise serializers.ValidationError({'numeros': f'Numeros indisponiveis: {indisponiveis}.'})

        transacao = Transacao.objects.create(
            rifa=rifa,
            vendedor=vendedor,
            data_expiracao=timezone.now() + timedelta(minutes=rifa.tempo_reserva),
            valor_total=rifa.valor_numero * len(numeros),
            **validated_data,
        )
        ItemTransacao.objects.bulk_create(
            ItemTransacao(
                transacao=transacao,
                numero=numero,
                valor_unitario=rifa.valor_numero,
            )
            for numero in numeros
        )
        NumeroRifa.objects.filter(pk__in=[numero.pk for numero in numeros]).update(
            status=NumeroRifa.Status.RESERVADO,
            atualizado_em=timezone.now(),
        )
        return transacao


class ReservaFormularioSerializer(ReservaSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('numeros', None)


class ItemTransacaoSerializer(serializers.ModelSerializer):
    numero = serializers.IntegerField(source='numero.numero', read_only=True)

    class Meta:
        model = ItemTransacao
        fields = ['id', 'numero', 'valor_unitario']


class TransacaoSerializer(serializers.ModelSerializer):
    itens = ItemTransacaoSerializer(many=True, read_only=True)
    vendedor_nome = serializers.CharField(source='vendedor.usuario.nome', read_only=True)

    class Meta:
        model = Transacao
        fields = [
            'id',
            'comprador_nome',
            'comprador_email',
            'comprador_telefone',
            'comprador_cpf',
            'vendedor',
            'vendedor_nome',
            'rifa',
            'data_expiracao',
            'status',
            'valor_total',
            'itens',
            'criado_em',
        ]
        read_only_fields = fields
