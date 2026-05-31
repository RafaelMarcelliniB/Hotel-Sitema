from core.base_repositories import BaseRepository
from users.models import AuditLog, Trabajador


class TrabajadorRepository(BaseRepository):
    model = Trabajador


class AuditLogRepository(BaseRepository):
    model = AuditLog

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula únicamente consultas y persistencia del módulo users.
# O - Open/Closed: nuevos repositorios concretos se agregan sin alterar la base genérica.
# L - Liskov Substitution: cualquier repositorio hijo puede sustituir a BaseRepository.
# I - Interface Segregation: cada entidad tiene su propio repositorio y no comparte contratos innecesarios.
# D - Dependency Inversion: los servicios consumen esta abstracción en lugar del ORM directo.
# ════════════════════════════════════════
