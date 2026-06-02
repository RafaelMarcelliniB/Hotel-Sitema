from django.db import transaction
from django.utils import timezone
from core.base_services import BaseService
from hotel.models import Habitacion, CheckIn
from hotel.repositories import CargoAdicionalRepository, CheckInRepository, CheckOutRepository, HabitacionRepository, HuespedRepository, ReservaRepository


class HabitacionService(BaseService):
    repository_class = HabitacionRepository


class HuespedService(BaseService):
    repository_class = HuespedRepository


class CheckInService(BaseService):
    repository_class = CheckInRepository

    def __init__(self):
        super().__init__()
        self.habitacion_repo = HabitacionRepository()

    @transaction.atomic
    def iniciar_alquiler(self, data):
        
        habitacion = self.habitacion_repo.get_by_id(data.get('habitacion'))
        
        if habitacion.estado_ocupacion != Habitacion.EstadoOcupacion.DISPONIBLE:
            raise ValueError("La habitación no está disponible.")

        #Crea el Check-In
        checkin = self.repository.create(**data)

        #Actualiza estado de habitación 
        self.habitacion_repo.update(habitacion.id, estado_ocupacion=Habitacion.EstadoOcupacion.OCUPADO)
        
        return checkin

class CheckOutService(BaseService):
    repository_class = CheckOutRepository

    @transaction.atomic
    def finalizar_alquiler(self, checkin_id, checkout_data):
        
        checkin_repo = CheckInRepository()
        habitacion_repo = HabitacionRepository()
        
        checkin = checkin_repo.get_by_id(checkin_id)

        #Cálculo del consumo total ya viene del modelo/vistas, 
        # aquí registramos el fin del proceso.
        checkout = self.repository.create(checkin=checkin, **checkout_data)

        #Actualiza Check-In
        checkin_repo.update(checkin.id, estado=CheckIn.Estado.CERRADO, 
                            fecha_salida_real=timezone.now().date(),
                            hora_salida_real=timezone.now().time())

        #Libera habitación y marcarla para limpieza (Estado SUCIO)
        habitacion_repo.update(checkin.habitacion.id, 
                                estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE,
                                estado_limpieza=Habitacion.EstadoLimpieza.SUCIO)
        return checkout

class CargoAdicionalService(BaseService):
    repository_class = CargoAdicionalRepository


class ReservaService(BaseService):
    repository_class = ReservaRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio del módulo hotel.
# O - Open/Closed: nuevas reglas de negocio se agregan en nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos pueden reemplazar a BaseService.
# I - Interface Segregation: cada caso de uso tiene su propio servicio.
# D - Dependency Inversion: las vistas dependen de servicios y no del ORM.
# ════════════════════════════════════════
