from core.base_services import BaseService
from market.repositories import DetalleVentaRepository, IngresoMercaderiaRepository, ProductoRepository, VentaMarketRepository


class ProductoService(BaseService):
    repository_class = ProductoRepository


class IngresoMercaderiaService(BaseService):
    repository_class = IngresoMercaderiaRepository


class VentaMarketService(BaseService):
    repository_class = VentaMarketRepository


class DetalleVentaService(BaseService):
    repository_class = DetalleVentaRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio del módulo market.
# O - Open/Closed: nuevos casos de uso se añaden con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos reemplazan a BaseService sin romper el flujo.
# I - Interface Segregation: cada servicio cubre un propósito específico.
# D - Dependency Inversion: las vistas dependen de servicios y no del ORM.
# ════════════════════════════════════════
