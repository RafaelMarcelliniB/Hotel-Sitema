from core.base_repositories import BaseRepository
from cochera.models import EspacioCochera, RegistroVehiculo


class EspacioCocheraRepository(BaseRepository):
    model = EspacioCochera

    def obtener_espacios_libres(self):
        
        return self.model.objects.filter(estado=EspacioCochera.Estado.LIBRE)

class RegistroVehiculoRepository(BaseRepository):
    model = RegistroVehiculo

    def obtener_vehiculos_en_cochera(self):
       
        return self.model.objects.filter(fecha_salida__isnull=True).select_related('espacio', 'trabajador')

    def filtrar_historial_por_fecha(self, fecha):
       
        return self.model.objects.filter(fecha_entrada=fecha).select_related('espacio', 'trabajador').order_by('-hora_entrada')
# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula acceso a datos del módulo cochera.
# O - Open/Closed: repositorios nuevos pueden añadirse sin tocar la base.
# L - Liskov Substitution: cada repositorio cumple el contrato CRUD.
# I - Interface Segregation: cada entidad de cochera conserva su propio repositorio.
# D - Dependency Inversion: los servicios dependen de esta abstracción y no del ORM.
# ════════════════════════════════════════
