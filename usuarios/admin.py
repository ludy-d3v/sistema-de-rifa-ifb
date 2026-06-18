from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'nome', 'papel', 'is_active', 'is_staff', 'ultimo_acesso')
    list_filter = ('papel', 'is_active', 'is_staff')
    search_fields = ('email', 'nome', 'telefone', 'cpf')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('nome', 'telefone', 'cpf', 'papel')}),
        ('Permissoes', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'ultimo_acesso', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'nome', 'papel', 'password1', 'password2'),
            },
        ),
    )
