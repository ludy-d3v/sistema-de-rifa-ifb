from rest_framework import permissions


class IsOrganizador(permissions.BasePermission):
    message = 'Apenas organizadores podem acessar este recurso.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.papel == 'organizador'
        )


class IsVendedor(permissions.BasePermission):
    message = 'Apenas vendedores podem acessar este recurso.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.papel == 'vendedor'
        )
