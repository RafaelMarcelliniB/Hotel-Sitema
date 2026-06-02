from core.base_repositories import BaseRepository
from hotel.models import CargoAdicional, CheckIn, CheckOut, Habitacion, Huesped, Reserva


class HabitacionRepository(BaseRepository):
    model = Habitacion

    def obtener_disponibles(self):
        """Requerimiento 3.5: Consulta de disponibilidad en tiempo real."""
        return self.model.objects.filter(
            estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE,
            estado_limpieza=Habitacion.EstadoLimpieza.LIMPIO
        )

class HuespedRepository(BaseRepository):
    model = Huesped


class CheckInRepository(BaseRepository):
    model = CheckIn

    def obtener_activos(self):
        """Retorna alquileres actuales (sin fecha de salida real)."""
        return self.model.objects.filter(estado=CheckIn.Estado.ACTIVO).select_related('habitacion', 'huesped')

class CheckOutRepository(BaseRepository):
    model = CheckOut


class CargoAdicionalRepository(BaseRepository):
    model = CargoAdicional


class ReservaRepository(BaseRepository):
    model = Reserva

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula acceso a datos del módulo hotel.
# O - Open/Closed: nuevos repositorios concretos se agregan sin cambiar la base.
# L - Liskov Substitution: cada repositorio concreto sustituye a BaseRepository.
# I - Interface Segregation: cada entidad mantiene su propio acceso a persistencia.
# D - Dependency Inversion: los servicios consumen esta abstracción de repositorio.
# ════════════════════════════════════════
