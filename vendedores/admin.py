from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from rifas.models import Transacao

from .models import DashboardVendedor, Vendedor, VendedorRifa

Usuario = get_user_model()


def usuario_organizador(user):
    return user.is_superuser or getattr(user, 'papel', None) == Usuario.Papel.ORGANIZADOR


class VendedorRifaInline(admin.TabularInline):
    model = VendedorRifa
    extra = 0
    fields = ('rifa', 'ativo', 'atualizado_em')
    readonly_fields = ('atualizado_em',)
    autocomplete_fields = ('rifa',)
    show_change_link = True


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'email',
        'organizador',
        'comissao_por_numero',
        'ativo',
        'total_rifas_associadas',
    )
    list_filter = ('ativo', 'organizador')
    search_fields = ('usuario__nome', 'usuario__email', 'organizador__nome', 'organizador__email')
    autocomplete_fields = ('usuario', 'organizador')
    list_select_related = ('usuario', 'organizador')
    inlines = (VendedorRifaInline,)
    fieldsets = (
        ('Dados do vendedor', {
            'fields': ('usuario', 'organizador', 'comissao_fixa', 'ativo'),
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('criado_em', 'atualizado_em')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'usuario':
            kwargs['queryset'] = Usuario.objects.filter(papel=Usuario.Papel.VENDEDOR, is_active=True)
        elif db_field.name == 'organizador':
            queryset = Usuario.objects.filter(papel=Usuario.Papel.ORGANIZADOR, is_active=True)
            if not request.user.is_superuser:
                queryset = queryset.filter(pk=request.user.pk)
            kwargs['queryset'] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(organizador=request.user)

    def has_module_permission(self, request):
        return usuario_organizador(request.user)

    def has_view_permission(self, request, obj=None):
        return usuario_organizador(request.user)

    def has_add_permission(self, request):
        return usuario_organizador(request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return usuario_organizador(request.user)
        return usuario_organizador(request.user) and obj.organizador_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.organizador = request.user
        obj.usuario.papel = Usuario.Papel.VENDEDOR
        obj.usuario.is_staff = True
        obj.usuario.save(update_fields=['papel', 'is_staff', 'atualizado_em'])
        super().save_model(request, obj, form, change)

    @admin.display(description='Nome', ordering='usuario__nome')
    def nome(self, obj):
        return obj.usuario.nome

    @admin.display(description='E-mail', ordering='usuario__email')
    def email(self, obj):
        return obj.usuario.email

    @admin.display(description='Comissao por numero', ordering='comissao_fixa')
    def comissao_por_numero(self, obj):
        return obj.comissao_fixa

    @admin.display(description='Rifas')
    def total_rifas_associadas(self, obj):
        return obj.rifas_associadas.filter(ativo=True).count()


@admin.register(VendedorRifa)
class VendedorRifaAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'rifa', 'organizador', 'associacao_ativa', 'atualizado_em')
    list_filter = ('ativo', 'rifa', 'vendedor__organizador')
    search_fields = ('vendedor__usuario__nome', 'rifa__titulo')
    autocomplete_fields = ('vendedor', 'rifa')
    list_select_related = ('vendedor', 'vendedor__usuario', 'vendedor__organizador', 'rifa')
    readonly_fields = ('criado_em', 'atualizado_em')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(vendedor__organizador=request.user)

    def has_module_permission(self, request):
        return usuario_organizador(request.user)

    def has_view_permission(self, request, obj=None):
        return usuario_organizador(request.user)

    def has_add_permission(self, request):
        return usuario_organizador(request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return usuario_organizador(request.user)
        return usuario_organizador(request.user) and obj.vendedor.organizador_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    @admin.display(description='Organizador', ordering='vendedor__organizador__nome')
    def organizador(self, obj):
        return obj.vendedor.organizador

    @admin.display(description='Associacao ativa', boolean=True, ordering='ativo')
    def associacao_ativa(self, obj):
        return obj.ativo


@admin.register(DashboardVendedor)
class DashboardVendedorAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'rifas_ativas',
        'total_vendas',
        'numeros_pagos',
        'numeros_pendentes',
        'valor_bruto',
        'comissao_estimada',
    )
    search_fields = ('usuario__nome', 'usuario__email')
    list_select_related = ('usuario', 'organizador')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if getattr(request.user, 'papel', None) == Usuario.Papel.VENDEDOR:
            return queryset.filter(usuario=request.user)
        return queryset.filter(organizador=request.user)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Vendedor', ordering='usuario__nome')
    def nome(self, obj):
        return obj.usuario.nome

    @admin.display(description='Rifas ativas')
    def rifas_ativas(self, obj):
        return obj.rifas_associadas.filter(ativo=True).count()

    @admin.display(description='Vendas')
    def total_vendas(self, obj):
        return obj.transacoes.count()

    @admin.display(description='Numeros pagos')
    def numeros_pagos(self, obj):
        return obj.transacoes.filter(status=Transacao.Status.PAGA).aggregate(
            total=Count('itens')
        )['total'] or 0

    @admin.display(description='Numeros pendentes')
    def numeros_pendentes(self, obj):
        return obj.transacoes.filter(
            status__in=[Transacao.Status.RESERVADA, Transacao.Status.AGUARDANDO_APROVACAO]
        ).aggregate(total=Count('itens'))['total'] or 0

    @admin.display(description='Valor bruto')
    def valor_bruto(self, obj):
        return obj.transacoes.filter(status=Transacao.Status.PAGA).aggregate(
            total=Sum('valor_total')
        )['total'] or 0

    @admin.display(description='Comissao estimada')
    def comissao_estimada(self, obj):
        return self.numeros_pagos(obj) * obj.comissao_fixa
