from django.conf import settings
from django.db import models

from rifas.models import Rifa


class Vendedor(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='usuario',
        on_delete=models.PROTECT,
        related_name='perfil_vendedor',
    )
    organizador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='organizador',
        on_delete=models.PROTECT,
        related_name='vendedores',
    )
    comissao_fixa = models.DecimalField('comissao por numero', max_digits=10, decimal_places=2)
    ativo = models.BooleanField('ativo', default=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

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
        verbose_name='vendedor',
        on_delete=models.CASCADE,
        related_name='rifas_associadas',
    )
    rifa = models.ForeignKey(
        Rifa,
        verbose_name='rifa',
        on_delete=models.CASCADE,
        related_name='vendedores_associados',
    )
    ativo = models.BooleanField('associacao ativa', default=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        ordering = ['rifa__titulo']
        verbose_name = 'rifa associada'
        verbose_name_plural = 'rifas associadas'
        constraints = [
            models.UniqueConstraint(
                fields=['vendedor', 'rifa'],
                name='associacao_unica_vendedor_rifa',
            ),
        ]

    def __str__(self):
        return f'{self.vendedor} - {self.rifa}'


class DashboardVendedor(Vendedor):
    class Meta:
        proxy = True
        verbose_name = 'dashboard do vendedor'
        verbose_name_plural = 'dashboard do vendedor'
