from django import forms
from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from django.utils.html import format_html
from urllib.parse import urlencode

from .models import ImagemRifa, ItemTransacao, NumeroRifa, Premio, Rifa, Transacao
from .services import expirar_reservas_vencidas


Usuario = get_user_model()

admin.site.site_header = 'RifaFacil - Painel Administrativo'
admin.site.site_title = 'RifaFacil Admin'
admin.site.index_title = 'Gestao interna'


def usuario_organizador(user):
    return user.is_superuser or getattr(user, 'papel', None) == 'organizador'


def usuario_vendedor(user):
    return getattr(user, 'papel', None) == 'vendedor'


class NumeroRifaInline(admin.TabularInline):
    model = NumeroRifa
    extra = 0
    fields = ('numero', 'status', 'atualizado_em')
    readonly_fields = ('numero', 'atualizado_em')
    max_num = 0
    can_delete = False
    show_change_link = True


class ImagemRifaInline(admin.TabularInline):
    model = ImagemRifa
    extra = 0
    fields = ('imagem', 'ordem')


class PremioAdminForm(forms.ModelForm):
    class Meta:
        model = Premio
        fields = '__all__'

    def clean_posicao(self):
        posicao = self.cleaned_data.get('posicao')
        if posicao and (posicao < 1 or posicao > 5):
            raise forms.ValidationError('A posicao do premio deve estar entre 1 e 5.')
        return posicao

    def clean(self):
        cleaned_data = super().clean()
        rifa = cleaned_data.get('rifa')
        posicao = cleaned_data.get('posicao')
        if not rifa:
            return cleaned_data

        premios = Premio.objects.filter(rifa=rifa)
        if self.instance.pk:
            premios = premios.exclude(pk=self.instance.pk)

        if premios.count() >= 5:
            raise forms.ValidationError('A rifa aceita no maximo 5 premios.')

        if posicao and premios.filter(posicao=posicao).exists():
            self.add_error('posicao', 'Ja existe premio nesta posicao.')

        return cleaned_data


class PremioInline(admin.TabularInline):
    model = Premio
    form = PremioAdminForm
    extra = 0
    max_num = 5
    fields = ('posicao', 'descricao', 'imagem')


class ItemTransacaoInline(admin.TabularInline):
    model = ItemTransacao
    extra = 0
    fields = ('numero', 'valor_unitario')
    readonly_fields = ('numero', 'valor_unitario')
    can_delete = False
    show_change_link = True


@admin.register(Rifa)
class RifaAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'organizador',
        'status',
        'valor_do_numero',
        'quantidade_total',
        'progresso_vendas',
        'atalho_numeros',
        'data_do_sorteio',
    )
    list_filter = ('status', 'data_sorteio')
    search_fields = ('titulo', 'slug', 'organizador__nome', 'organizador__email')
    readonly_fields = (
        'slug',
        'progresso_vendas',
        'atalho_numeros',
        'criado_em',
        'atualizado_em',
        'excluido_em',
    )
    autocomplete_fields = ('organizador',)
    inlines = (ImagemRifaInline, PremioInline)
    fieldsets = (
        ('Dados principais', {
            'fields': (
                'titulo',
                'slug',
                'descricao',
                'descricao_html',
                'imagem_principal',
                'organizador',
            ),
        }),
        ('Configuracao da rifa', {
            'fields': (
                'valor_numero',
                'total_numeros',
                'data_sorteio',
                'chave_pix',
                'tempo_reserva',
                'link_transmissao',
            ),
        }),
        ('Publicacao e controle', {
            'fields': ('status', 'progresso_vendas', 'atalho_numeros'),
        }),
        ('Auditoria', {
            'fields': ('excluido_em', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if usuario_vendedor(request.user):
            return queryset.filter(
                vendedores_associados__vendedor__usuario=request.user,
                vendedores_associados__ativo=True,
            ).distinct()
        return queryset.filter(organizador=request.user)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'organizador' and not request.user.is_superuser:
            kwargs['queryset'] = Usuario.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if usuario_vendedor(request.user):
            return tuple(
                dict.fromkeys(
                    [field.name for field in self.model._meta.fields]
                    + ['progresso_vendas']
                )
            )
        if obj:
            readonly_fields.append('total_numeros')
            if obj.possui_vendas:
                readonly_fields.append('valor_numero')
        return tuple(dict.fromkeys(readonly_fields))

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if not request.user.is_superuser:
                obj.organizador = request.user
            super().save_model(request, obj, form, change)
            if not change and not obj.numeros.exists():
                numeros = [
                    NumeroRifa(rifa=obj, numero=numero)
                    for numero in range(1, obj.total_numeros + 1)
                ]
                NumeroRifa.objects.bulk_create(numeros)

    @admin.display(description='Progresso')
    def progresso_vendas(self, obj):
        if not obj.pk:
            return '0/0 (0%)'
        total = obj.numeros.count()
        if total == 0:
            return '0/0 (0%)'
        pagos = obj.numeros.filter(status=NumeroRifa.Status.PAGO).count()
        percentual = (pagos / total) * 100
        return f'{pagos}/{total} ({percentual:.1f}%)'

    @admin.display(description='Numeros')
    def atalho_numeros(self, obj):
        if not obj.pk:
            return 'Salve a rifa para gerar e visualizar os numeros.'
        url = reverse('admin:rifas_numerorifa_changelist')
        query = urlencode({'rifa__id__exact': obj.pk})
        return format_html('<a class="button" href="{}?{}">Ver numeros desta rifa</a>', url, query)

    @admin.display(description='Valor do numero', ordering='valor_numero')
    def valor_do_numero(self, obj):
        return obj.valor_numero

    @admin.display(description='Total de numeros', ordering='total_numeros')
    def quantidade_total(self, obj):
        return obj.total_numeros

    @admin.display(description='Data do sorteio', ordering='data_sorteio')
    def data_do_sorteio(self, obj):
        return obj.data_sorteio


@admin.register(NumeroRifa)
class NumeroRifaAdmin(admin.ModelAdmin):
    list_display = ('rifa', 'numero_da_rifa', 'status', 'atualizado_em')
    list_display_links = ('rifa', 'numero_da_rifa')
    list_filter = ('status', 'rifa')
    search_fields = ('rifa__titulo', 'numero')
    autocomplete_fields = ('rifa',)
    list_select_related = ('rifa',)
    ordering = ('rifa__titulo', 'numero')
    list_per_page = 50
    fields = ('rifa', 'numero', 'status', 'criado_em', 'atualizado_em')
    readonly_fields = ('rifa', 'numero', 'status', 'criado_em', 'atualizado_em')

    @admin.display(description='Numero', ordering='numero')
    def numero_da_rifa(self, obj):
        return obj.numero

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if usuario_vendedor(request.user):
            return queryset.filter(
                rifa__vendedores_associados__vendedor__usuario=request.user,
                rifa__vendedores_associados__ativo=True,
            ).distinct()
        return queryset.filter(rifa__organizador=request.user)

    def has_module_permission(self, request):
        return request.user.is_staff and not usuario_vendedor(request.user)

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return usuario_organizador(request.user)
        return usuario_organizador(request.user) and obj.rifa.organizador_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    form = PremioAdminForm
    list_display = ('rifa', 'posicao', 'descricao')
    list_filter = ('posicao', 'rifa')
    search_fields = ('rifa__titulo', 'descricao')
    autocomplete_fields = ('rifa',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if usuario_vendedor(request.user):
            return queryset.filter(
                rifa__vendedores_associados__vendedor__usuario=request.user,
                rifa__vendedores_associados__ativo=True,
            ).distinct()
        return queryset.filter(rifa__organizador=request.user)

    def has_module_permission(self, request):
        return request.user.is_staff and not usuario_vendedor(request.user)

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return usuario_organizador(request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return usuario_organizador(request.user)
        return usuario_organizador(request.user) and obj.rifa.organizador_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)


def atualizar_transacoes(queryset, status_transacao, status_numero):
    atualizadas = 0
    with transaction.atomic():
        for transacao_obj in queryset.prefetch_related('itens__numero'):
            transacao_obj.status = status_transacao
            transacao_obj.save(update_fields=['status', 'atualizado_em'])
            atualizar_numeros_da_transacao(transacao_obj)
            atualizadas += 1
    return atualizadas


def status_numero_por_status_transacao(status_transacao):
    mapa_status = {
        Transacao.Status.RESERVADA: NumeroRifa.Status.RESERVADO,
        Transacao.Status.AGUARDANDO_APROVACAO: NumeroRifa.Status.AGUARDANDO_APROVACAO,
        Transacao.Status.PAGA: NumeroRifa.Status.PAGO,
        Transacao.Status.EXPIRADA: NumeroRifa.Status.DISPONIVEL,
        Transacao.Status.REJEITADA: NumeroRifa.Status.DISPONIVEL,
    }
    return mapa_status.get(status_transacao)


def atualizar_numeros_da_transacao(transacao_obj):
    status_numero = status_numero_por_status_transacao(transacao_obj.status)
    if not status_numero:
        return 0
    numeros_ids = transacao_obj.itens.values_list('numero_id', flat=True)
    return NumeroRifa.objects.filter(id__in=numeros_ids).update(
        status=status_numero,
        atualizado_em=transacao_obj.atualizado_em,
    )


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = (
        'comprador',
        'rifa',
        'vendedor',
        'status',
        'valor_da_venda',
        'quantidade_numeros',
        'expira_em',
        'criada_em',
    )
    list_filter = ('status', 'rifa', 'vendedor')
    search_fields = ('comprador_nome', 'comprador_email', 'comprador_cpf', 'rifa__titulo')
    readonly_fields = ('comprovante_enviado', 'criado_em', 'atualizado_em')
    autocomplete_fields = ('rifa', 'vendedor')
    list_select_related = ('rifa', 'vendedor', 'vendedor__usuario')
    inlines = (ItemTransacaoInline,)
    actions = (
        'marcar_aguardando_aprovacao',
        'marcar_paga',
        'marcar_rejeitada',
        'expirar_reservas_vencidas_action',
    )
    fieldsets = (
        ('Comprador', {
            'fields': (
                'comprador_nome',
                'comprador_email',
                'comprador_telefone',
                'comprador_cpf',
            ),
        }),
        ('Venda', {
            'fields': (
                'rifa',
                'vendedor',
                'status',
                'valor_total',
                'data_expiracao',
                'comprovante_enviado',
            ),
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if usuario_vendedor(request.user):
            return queryset.filter(vendedor__usuario=request.user)
        return queryset.filter(rifa__organizador=request.user)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return usuario_organizador(request.user)
        return usuario_organizador(request.user) and obj.rifa.organizador_id == request.user.id

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not usuario_organizador(request.user):
            return {}
        return actions

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            if change and 'status' in form.changed_data:
                total = atualizar_numeros_da_transacao(obj)
                self.message_user(
                    request,
                    f'Status da transacao atualizado. {total} numero(s) sincronizado(s).',
                    messages.SUCCESS,
                )

    @admin.display(description='Numeros')
    def quantidade_numeros(self, obj):
        return obj.itens.count()

    @admin.display(description='Comprador', ordering='comprador_nome')
    def comprador(self, obj):
        return obj.comprador_nome

    @admin.display(description='Valor total', ordering='valor_total')
    def valor_da_venda(self, obj):
        return obj.valor_total

    @admin.display(description='Expira em', ordering='data_expiracao')
    def expira_em(self, obj):
        return obj.data_expiracao

    @admin.display(description='Criada em', ordering='criado_em')
    def criada_em(self, obj):
        return obj.criado_em

    @admin.display(description='Comprovante')
    def comprovante_enviado(self, obj):
        if not obj.comprovante:
            return 'Nenhum comprovante enviado.'
        return format_html('<a class="button" href="{}" target="_blank">Ver comprovante</a>', obj.comprovante.url)

    @admin.action(description='Marcar como aguardando aprovacao')
    def marcar_aguardando_aprovacao(self, request, queryset):
        total = atualizar_transacoes(
            queryset,
            Transacao.Status.AGUARDANDO_APROVACAO,
            NumeroRifa.Status.AGUARDANDO_APROVACAO,
        )
        self.message_user(request, f'{total} transacao(oes) atualizada(s).', messages.SUCCESS)

    @admin.action(description='Marcar como paga')
    def marcar_paga(self, request, queryset):
        total = atualizar_transacoes(
            queryset,
            Transacao.Status.PAGA,
            NumeroRifa.Status.PAGO,
        )
        self.message_user(request, f'{total} transacao(oes) marcada(s) como paga(s).', messages.SUCCESS)

    @admin.action(description='Marcar como rejeitada e liberar numeros')
    def marcar_rejeitada(self, request, queryset):
        total = atualizar_transacoes(
            queryset,
            Transacao.Status.REJEITADA,
            NumeroRifa.Status.DISPONIVEL,
        )
        self.message_user(request, f'{total} transacao(oes) rejeitada(s). Numeros liberados.', messages.SUCCESS)

    @admin.action(description='Expirar reservas vencidas')
    def expirar_reservas_vencidas_action(self, request, queryset):
        reservas_expiradas, numeros_liberados = expirar_reservas_vencidas()
        self.message_user(
            request,
            f'{reservas_expiradas} reserva(s) expirada(s); {numeros_liberados} numero(s) liberado(s).',
            messages.SUCCESS,
        )
