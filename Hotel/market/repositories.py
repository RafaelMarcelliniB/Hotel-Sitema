from core.base_repositories import BaseRepository
from market.models import DetalleVenta, IngresoMercaderia, Producto, VentaMarket


class ProductoRepository(BaseRepository):
    model = Producto

    def get_productos_activos(self):
        return self.model.objects.filter(activo=True)

class IngresoMercaderiaRepository(BaseRepository):
    model = IngresoMercaderia


class VentaMarketRepository(BaseRepository):
    model = VentaMarket

    def obtener_historial_filtrado(self, fecha_inicio=None, fecha_fin=None, producto_id=None):
       
        queryset = self.model.objects.all().select_related('trabajador').prefetch_related('detalles__producto')

        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
        
        if producto_id:
            # Filtra ventas que contengan ese producto específico en sus detalles
            queryset = queryset.filter(detalles__producto_id=producto_id).distinct()

        return queryset.order_by('-fecha', '-hora')
    
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
