from core.base_services import BaseService
from hotel.repositories import CargoAdicionalRepository, CheckInRepository, CheckOutRepository, HabitacionRepository, HuespedRepository, ReservaRepository


class HabitacionService(BaseService):
    repository_class = HabitacionRepository


class HuespedService(BaseService):
    repository_class = HuespedRepository


class CheckInService(BaseService):
    repository_class = CheckInRepository


class CheckOutService(BaseService):
    repository_class = CheckOutRepository


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
