from django.conf import settings
from django.db import models

from rifas.models import Rifa


class Vendedor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='perfil_vendedor',
    )
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='vendedores',
    )
    comissao_fixa = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['usuario__nome']
        verbose_name = 'vendedor'
        verbose_name_plural = 'vendedores'
        constraints = [
            models.UniqueConstraint(
                fields=['organizador', 'usuario'],
                name='vendedor_unico_por_organizador',
            ),
        ]

    def __str__(self):
        return self.usuario.nome


class VendedorRifa(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        on_delete=models.CASCADE,
        related_name='rifas_associadas',
    )
    rifa = models.ForeignKey(
        Rifa,
        on_delete=models.CASCADE,
        related_name='vendedores_associados',
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['rifa__titulo']
        verbose_name = 'associacao vendedor-rifa'
        verbose_name_plural = 'associacoes vendedor-rifa'
        constraints = [
            models.UniqueConstraint(
                fields=['vendedor', 'rifa'],
                name='associacao_unica_vendedor_rifa',
            ),
        ]

    def __str__(self):
        return f'{self.vendedor} - {self.rifa}'
