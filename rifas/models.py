from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Rifa(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = 'rascunho', 'Rascunho'
        ATIVA = 'ativa', 'Ativa'
        ENCERRADA = 'encerrada', 'Encerrada'

    titulo = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    descricao_html = models.TextField(blank=True)
    valor_numero = models.DecimalField(max_digits=10, decimal_places=2)
    total_numeros = models.PositiveIntegerField()
    data_sorteio = models.DateTimeField()
    chave_pix = models.CharField(max_length=150)
    tempo_reserva = models.PositiveIntegerField(default=15)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RASCUNHO)
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='rifas',
    )
    imagem_principal = models.FileField(upload_to='rifas/principais/', blank=True)
    link_transmissao = models.URLField(blank=True)
    ativo = models.BooleanField(default=True)
    excluido_em = models.DateTimeField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'rifa'
        verbose_name_plural = 'rifas'

    def __str__(self):
        return self.titulo

    @property
    def possui_vendas(self):
        return self.numeros.filter(status=NumeroRifa.Status.VENDIDO).exists()

    def soft_delete(self):
        if self.possui_vendas:
            raise ValidationError('Rifas com vendas nao podem ser excluidas.')
        self.ativo = False
        self.excluido_em = timezone.now()
        self.save(update_fields=['ativo', 'excluido_em', 'atualizado_em'])


class NumeroRifa(models.Model):
    class Status(models.TextChoices):
        DISPONIVEL = 'disponivel', 'Disponivel'
        RESERVADO = 'reservado', 'Reservado'
        VENDIDO = 'vendido', 'Vendido'

    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE, related_name='numeros')
    numero = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DISPONIVEL)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rifa', 'numero'], name='numero_unico_por_rifa'),
        ]
        ordering = ['numero']
        verbose_name = 'numero da rifa'
        verbose_name_plural = 'numeros da rifa'

    def __str__(self):
        return f'{self.rifa} - {self.numero}'


class ImagemRifa(models.Model):
    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE, related_name='imagens_galeria')
    imagem = models.FileField(upload_to='rifas/galeria/')
    ordem = models.PositiveSmallIntegerField(default=1)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'imagem da galeria'
        verbose_name_plural = 'imagens da galeria'

    def __str__(self):
        return f'Imagem {self.ordem} - {self.rifa}'


class Premio(models.Model):
    rifa = models.ForeignKey(Rifa, on_delete=models.CASCADE, related_name='premios')
    posicao = models.PositiveSmallIntegerField()
    descricao = models.TextField()
    imagem = models.FileField(upload_to='rifas/premios/', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['rifa', 'posicao'], name='premio_unico_por_posicao'),
        ]
        ordering = ['posicao']
        verbose_name = 'premio'
        verbose_name_plural = 'premios'

    def __str__(self):
        return f'{self.posicao}o premio - {self.rifa}'
