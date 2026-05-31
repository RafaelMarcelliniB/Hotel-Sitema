from core.base_repositories import BaseRepository
from market.models import DetalleVenta, IngresoMercaderia, Producto, VentaMarket


class ProductoRepository(BaseRepository):
    model = Producto


class IngresoMercaderiaRepository(BaseRepository):
    model = IngresoMercaderia


class VentaMarketRepository(BaseRepository):
    model = VentaMarket


class DetalleVentaRepository(BaseRepository):
    model = DetalleVenta

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: encapsula persistencia y consultas del módulo market.
# O - Open/Closed: repositorios nuevos se agregan sin modificar la base.
# L - Liskov Substitution: cada repositorio cumple el contrato CRUD esperado.
# I - Interface Segregation: cada entidad tiene su propio repositorio.
# D - Dependency Inversion: los servicios dependen de esta capa y no del ORM directo.
# ════════════════════════════════════════
