from core.base_services import BaseService
from recados.repositories import RecadoRepository


class RecadoService(BaseService):
    repository_class = RecadoRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio del módulo recados.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: el servicio hijo puede reemplazar a BaseService.
# I - Interface Segregation: cubre una única responsabilidad de negocio.
# D - Dependency Inversion: la vista depende de este servicio y no del ORM.
# ════════════════════════════════════════
