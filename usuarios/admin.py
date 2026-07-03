from django import forms
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from vendedores.models import Vendedor

from .models import Usuario


admin.site.unregister(Group)


@admin.register(Group)
class GrupoAdmin(GroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser


class UsuarioCriacaoAdminForm(UserCreationForm):
    telefone = forms.CharField(label='Telefone', max_length=20, required=False)
    cpf = forms.CharField(label='CPF', max_length=14, required=False)
    organizador_vendedor = forms.ModelChoiceField(
        label='Organizador responsavel',
        queryset=Usuario.objects.none(),
        required=False,
    )
    comissao_fixa = forms.DecimalField(
        label='Comissao fixa',
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0,
    )

    class Meta:
        model = Usuario
        fields = ('email', 'nome', 'telefone', 'cpf', 'papel')

    class Media:
        js = ('usuarios/admin_usuario_criacao.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizador_vendedor'].queryset = Usuario.objects.filter(
            papel=Usuario.Papel.ORGANIZADOR,
            is_active=True,
        )

    def clean(self):
        cleaned_data = super().clean()
        papel = cleaned_data.get('papel')

        if papel == Usuario.Papel.VENDEDOR:
            if not cleaned_data.get('organizador_vendedor'):
                self.add_error('organizador_vendedor', 'Informe o organizador responsavel pelo vendedor.')
            if cleaned_data.get('comissao_fixa') is None:
                self.add_error('comissao_fixa', 'Informe a comissao fixa do vendedor.')

        return cleaned_data


class PerfilVendedorInline(admin.StackedInline):
    model = Vendedor
    fk_name = 'usuario'
    extra = 0
    max_num = 1
    fields = ('organizador', 'comissao_fixa', 'ativo', 'criado_em', 'atualizado_em')
    readonly_fields = ('criado_em', 'atualizado_em')
    autocomplete_fields = ('organizador',)
    verbose_name = 'perfil de vendedor'
    verbose_name_plural = 'perfil de vendedor'

    def has_add_permission(self, request, obj):
        return bool(obj and obj.papel == Usuario.Papel.VENDEDOR and not hasattr(obj, 'perfil_vendedor'))

    def has_change_permission(self, request, obj=None):
        return bool(obj and obj.papel == Usuario.Papel.VENDEDOR)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'organizador' and not request.user.is_superuser:
            kwargs['queryset'] = Usuario.objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    add_form = UsuarioCriacaoAdminForm
    list_display = ('email', 'nome', 'papel', 'telefone', 'ativo', 'acesso_admin', 'ultimo_acesso')
    list_filter = ('papel', 'is_active', 'is_staff')
    search_fields = ('email', 'nome', 'telefone', 'cpf')
    ordering = ('email',)
    readonly_fields = ('last_login', 'ultimo_acesso', 'date_joined', 'criado_em', 'atualizado_em')
    inlines = (PerfilVendedorInline,)
    actions = ('redefinir_senha_padrao',)

    @admin.display(description='Ativo', boolean=True, ordering='is_active')
    def ativo(self, obj):
        return obj.is_active

    @admin.display(description='Acesso ao admin', boolean=True, ordering='is_staff')
    def acesso_admin(self, obj):
        return obj.is_staff

    def get_inline_instances(self, request, obj=None):
        if not obj or obj.papel != Usuario.Papel.VENDEDOR:
            return []
        if not request.user.is_superuser and getattr(request.user, 'papel', None) != Usuario.Papel.ORGANIZADOR:
            return []
        return super().get_inline_instances(request, obj)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR:
            return queryset.filter(
                id=request.user.id,
            ) | queryset.filter(
                perfil_vendedor__organizador=request.user,
            )
        return queryset.filter(id=request.user.id)

    def has_module_permission(self, request):
        return request.user.is_superuser or getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR
        if obj.id == request.user.id:
            return True
        return (
            getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR
            and hasattr(obj, 'perfil_vendedor')
            and obj.perfil_vendedor.organizador_id == request.user.id
        )

    def has_add_permission(self, request):
        return request.user.is_superuser or getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR
        if obj.id == request.user.id:
            return True
        return (
            getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR
            and hasattr(obj, 'perfil_vendedor')
            and obj.perfil_vendedor.organizador_id == request.user.id
        )

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR
        return (
            getattr(request.user, 'papel', None) == Usuario.Papel.ORGANIZADOR
            and hasattr(obj, 'perfil_vendedor')
            and obj.perfil_vendedor.organizador_id == request.user.id
        )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if not request.user.is_superuser and obj and obj.id == request.user.id:
            readonly_fields.extend(['papel', 'is_staff', 'is_superuser', 'groups', 'user_permissions'])
        return tuple(dict.fromkeys(readonly_fields))

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('nome', 'telefone', 'cpf', 'papel')}),
        ('Permissoes', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'ultimo_acesso', 'date_joined', 'criado_em', 'atualizado_em')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'nome',
                    'telefone',
                    'cpf',
                    'papel',
                    'organizador_vendedor',
                    'comissao_fixa',
                    'password1',
                    'password2',
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if obj.papel in [Usuario.Papel.ORGANIZADOR, Usuario.Papel.VENDEDOR]:
            obj.is_staff = True
        super().save_model(request, obj, form, change)

        if not change and obj.papel == Usuario.Papel.VENDEDOR:
            Vendedor.objects.update_or_create(
                usuario=obj,
                defaults={
                    'organizador': form.cleaned_data['organizador_vendedor'],
                    'comissao_fixa': form.cleaned_data['comissao_fixa'],
                    'ativo': True,
                },
            )

    @admin.action(description='Redefinir senha para 12345678')
    def redefinir_senha_padrao(self, request, queryset):
        total = 0
        for usuario in queryset:
            usuario.set_password('12345678')
            usuario.save(update_fields=['password'])
            total += 1
        self.message_user(request, f'Senha redefinida para 12345678 em {total} usuario(s).')
