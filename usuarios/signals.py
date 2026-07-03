from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.db.utils import OperationalError, ProgrammingError
from django.dispatch import receiver

from .models import Usuario


GRUPO_ORGANIZADORES = 'Organizadores'
GRUPO_VENDEDORES = 'Vendedores'

PERMISSOES_ORGANIZADOR = {
    'usuarios.usuario': ['add', 'view', 'change', 'delete'],
    'rifas.rifa': ['add', 'view', 'change', 'delete'],
    'rifas.numerorifa': ['view', 'change'],
    'rifas.premio': ['add', 'view', 'change', 'delete'],
    'rifas.transacao': ['view', 'change'],
    'rifas.itemtransacao': ['view'],
    'vendedores.vendedor': ['add', 'view', 'change', 'delete'],
    'vendedores.vendedorrifa': ['add', 'view', 'change', 'delete'],
}

PERMISSOES_VENDEDOR = {
    'rifas.rifa': ['view'],
    'rifas.numerorifa': ['view'],
    'rifas.premio': ['view'],
    'rifas.transacao': ['view'],
    'rifas.itemtransacao': ['view'],
}


def configurar_permissoes_grupo(grupo, permissoes_por_modelo):
    permissoes = []
    for modelo, acoes in permissoes_por_modelo.items():
        app_label, model = modelo.split('.')
        content_type = ContentType.objects.filter(app_label=app_label, model=model).first()
        if not content_type:
            continue
        codenames = [f'{acao}_{model}' for acao in acoes]
        permissoes.extend(Permission.objects.filter(content_type=content_type, codename__in=codenames))
    grupo.permissions.set(permissoes)


def garantir_grupos_papeis():
    grupo_organizadores, _ = Group.objects.get_or_create(name=GRUPO_ORGANIZADORES)
    grupo_vendedores, _ = Group.objects.get_or_create(name=GRUPO_VENDEDORES)
    configurar_permissoes_grupo(grupo_organizadores, PERMISSOES_ORGANIZADOR)
    configurar_permissoes_grupo(grupo_vendedores, PERMISSOES_VENDEDOR)
    return grupo_organizadores, grupo_vendedores


@receiver(post_save, sender=Usuario)
def sincronizar_grupo_por_papel(sender, instance, **kwargs):
    try:
        grupo_organizadores, grupo_vendedores = garantir_grupos_papeis()
    except (OperationalError, ProgrammingError):
        return

    if instance.papel in [Usuario.Papel.ORGANIZADOR, Usuario.Papel.VENDEDOR] and not instance.is_staff:
        Usuario.objects.filter(pk=instance.pk).update(is_staff=True)

    instance.groups.remove(grupo_organizadores, grupo_vendedores)
    if instance.papel == Usuario.Papel.ORGANIZADOR:
        instance.groups.add(grupo_organizadores)
    elif instance.papel == Usuario.Papel.VENDEDOR:
        instance.groups.add(grupo_vendedores)
