from django.contrib import admin

from .models import Vendedor, VendedorRifa


class VendedorRifaInline(admin.TabularInline):
    model = VendedorRifa
    extra = 0
    fields = ('rifa', 'ativo')


@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'organizador', 'comissao_fixa', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('usuario__nome', 'usuario__email', 'organizador__nome', 'organizador__email')
    inlines = (VendedorRifaInline,)


@admin.register(VendedorRifa)
class VendedorRifaAdmin(admin.ModelAdmin):
    list_display = ('vendedor', 'rifa', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('vendedor__usuario__nome', 'rifa__titulo')
