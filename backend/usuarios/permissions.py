from rest_framework.permissions import BasePermission


# ── Solo Administradores pueden acceder ──
class SoloAdministrador(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol == 'Administrador'
        )


# ── Administradores y Empleados pueden acceder ──
class AdministradorOEmpleado(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.rol in ['Administrador', 'Empleado']
        )