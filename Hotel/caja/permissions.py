"""
Permisos personalizados para validar estado de caja.

CAJA ABIERTA PERMISSION:
- Restringe operaciones de venta/cobro a empleados con caja activa
- Admins SIEMPRE pueden operar (sin restricciones)
- Empleados sin caja abierta reciben ValidationError
"""

from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from caja.models import Caja
from users.models import Trabajador


class CajaAbertaPermission(permissions.BasePermission):
    """
    Permiso que valida que el usuario tiene una caja abierta.
    
    Aplicar a vistas con:
        permission_classes = [IsAuthenticated, CajaAbertaPermission]
    
    Comportamiento:
    - ADMIN: Acceso permitido sin caja (operaciones globales)
    - CAJERO/RECEPCIONISTA: Requiere caja ABIERTA asignada
    
    Si no tiene caja abierta, se lanza ValidationError con mensaje limpio.
    """
    
    def has_permission(self, request, view):
        """
        Verifica que el usuario tenga una caja abierta.
        
        Solo restringe en métodos que MODIFICAN datos (POST, PUT, PATCH, DELETE).
        GET siempre permitido.
        """
        
        # Permitir lectura (GET) sin restricciones
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Si es ADMIN, permitir TODO sin validación
        if hasattr(request.user, 'rol') and request.user.rol == Trabajador.Rol.ADMIN:
            return True
        
        hoy = timezone.localdate()
        turno_usuario = getattr(request.user, 'turno', None)

        filtros = {
            'trabajador': request.user,
            'estado': Caja.Estado.ABIERTA,
            'fecha_apertura': hoy,
        }
        if turno_usuario:
            filtros['turno'] = turno_usuario

        # Para empleados: validar misma lógica de caja activa (usuario + fecha local + turno)
        caja_abierta = Caja.objects.filter(**filtros).exists()

        if not caja_abierta:
            # Fallback controlado al mismo usuario y fecha local por cambio de turno en perfil
            caja_abierta = Caja.objects.filter(
                trabajador=request.user,
                estado=Caja.Estado.ABIERTA,
                fecha_apertura=hoy,
            ).exists()
        
        if not caja_abierta:
            raise ValidationError(
                "Debe aperturar su caja de turno antes de realizar esta operación."
            )
        
        return True


class CajaAbertaPermisoAlternativo(permissions.BasePermission):
    """
    Versión alternativa: Retorna False en lugar de lanzar excepción.
    
    Útil si prefieres manejar el error en la vista.
    No se recomienda - es mejor usar CajaAbertaPermission (más explícito).
    """
    
    def has_permission(self, request, view):
        # Permitir lectura
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Admin siempre puede
        if hasattr(request.user, 'rol') and request.user.rol == Trabajador.Rol.ADMIN:
            return True
        
        hoy = timezone.localdate()
        turno_usuario = getattr(request.user, 'turno', None)

        filtros = {
            'trabajador': request.user,
            'estado': Caja.Estado.ABIERTA,
            'fecha_apertura': hoy,
        }
        if turno_usuario:
            filtros['turno'] = turno_usuario

        # Empleado sin caja: rechazar
        caja_abierta = Caja.objects.filter(**filtros).exists()
        if not caja_abierta:
            caja_abierta = Caja.objects.filter(
                trabajador=request.user,
                estado=Caja.Estado.ABIERTA,
                fecha_apertura=hoy,
            ).exists()
        
        return caja_abierta


# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: validar caja abierta únicamente
# O - Open/Closed: nuevas reglas de caja se agregan sin modificar base
# L - Liskov Substitution: ambos permisos sustituyen BasePermission
# I - Interface Segregation: interfaz clara: tienes caja o no
# D - Dependency Inversion: depende de modelo Caja (abstracción)
# ════════════════════════════════════════
