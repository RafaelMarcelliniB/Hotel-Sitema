from core.base_services import BaseService
from cochera.repositories import EspacioCocheraRepository, RegistroVehiculoRepository


class EspacioCocheraService(BaseService):
    repository_class = EspacioCocheraRepository


class RegistroVehiculoService(BaseService):
    repository_class = RegistroVehiculoRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio de cochera.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos sustituyen a BaseService sin romper.
# I - Interface Segregation: cada servicio cubre una responsabilidad concreta.
# D - Dependency Inversion: la vista depende de servicios, no del ORM.
# ════════════════════════════════════════
