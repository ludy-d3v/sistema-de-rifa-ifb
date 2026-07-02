from django.db import transaction
from rest_framework import serializers

from .models import ImagemRifa, NumeroRifa, Premio, Rifa


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
