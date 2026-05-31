from core.base_services import BaseService
from caja.repositories import CajaRepository, MovimientoCajaRepository


class CajaService(BaseService):
    repository_class = CajaRepository


class MovimientoCajaService(BaseService):
    repository_class = MovimientoCajaRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio de caja.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos sustituyen a BaseService sin romper.
# I - Interface Segregation: cada servicio cubre una sola responsabilidad concreta.
# D - Dependency Inversion: la vista depende de servicios y no del ORM.
# ════════════════════════════════════════
