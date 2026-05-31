from core.base_repositories import BaseRepository
from cochera.models import EspacioCochera, RegistroVehiculo


class EspacioCocheraRepository(BaseRepository):
    model = EspacioCochera


class RegistroVehiculoRepository(BaseRepository):
    model = RegistroVehiculo

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula acceso a datos del módulo cochera.
# O - Open/Closed: repositorios nuevos pueden añadirse sin tocar la base.
# L - Liskov Substitution: cada repositorio cumple el contrato CRUD.
# I - Interface Segregation: cada entidad de cochera conserva su propio repositorio.
# D - Dependency Inversion: los servicios dependen de esta abstracción y no del ORM.
# ════════════════════════════════════════
