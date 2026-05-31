from core.base_repositories import BaseRepository
from recados.models import Recado


class RecadoRepository(BaseRepository):
    model = Recado

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula persistencia del módulo recados.
# O - Open/Closed: nuevos repositorios se agregan sin tocar la base.
# L - Liskov Substitution: el repositorio cumple el contrato CRUD.
# I - Interface Segregation: solo expone lo necesario para recados.
# D - Dependency Inversion: los servicios dependen de esta abstracción y no del ORM.
# ════════════════════════════════════════
