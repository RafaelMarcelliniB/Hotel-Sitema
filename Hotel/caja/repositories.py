from core.base_repositories import BaseRepository
from caja.models import Caja, MovimientoCaja


class CajaRepository(BaseRepository):
    model = Caja


class MovimientoCajaRepository(BaseRepository):
    model = MovimientoCaja

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula persistencia del módulo caja.
# O - Open/Closed: repositorios nuevos se agregan sin tocar la base.
# L - Liskov Substitution: cada repositorio cumple el contrato CRUD.
# I - Interface Segregation: cada entidad de caja conserva su propio acceso a datos.
# D - Dependency Inversion: los servicios dependen de esta capa y no del ORM.
# ════════════════════════════════════════
