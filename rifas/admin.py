from django.contrib import admin

from .models import ImagemRifa, NumeroRifa, Premio, Rifa


class NumeroRifaInline(admin.TabularInline):
    model = NumeroRifa
    extra = 0
    fields = ('numero', 'status')
    readonly_fields = ('numero',)
    max_num = 0


class ImagemRifaInline(admin.TabularInline):
    model = ImagemRifa
    extra = 0
    fields = ('imagem', 'ordem')


class PremioInline(admin.TabularInline):
    model = Premio
    extra = 0
    fields = ('posicao', 'descricao', 'imagem')


@admin.register(Rifa)
class RifaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizador', 'status', 'ativo', 'total_numeros', 'valor_numero')
    list_filter = ('status', 'ativo')
    search_fields = ('titulo', 'organizador__nome', 'organizador__email')
    readonly_fields = ('criado_em', 'atualizado_em', 'excluido_em')
    inlines = (ImagemRifaInline, PremioInline, NumeroRifaInline)


@admin.register(NumeroRifa)
class NumeroRifaAdmin(admin.ModelAdmin):
    list_display = ('rifa', 'numero', 'status')
    list_filter = ('status',)
    search_fields = ('rifa__titulo', 'numero')


@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    list_display = ('rifa', 'posicao', 'descricao')
    list_filter = ('posicao',)
    search_fields = ('rifa__titulo', 'descricao')
