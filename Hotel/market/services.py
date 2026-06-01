from django.db import transaction
from core.base_services import BaseService
from market.repositories import DetalleVentaRepository, IngresoMercaderiaRepository, ProductoRepository, VentaMarketRepository


class ProductoService(BaseService):
    repository_class = ProductoRepository


class IngresoMercaderiaService(BaseService):
    repository_class = IngresoMercaderiaRepository


class VentaMarketService(BaseService):
    repository_class = VentaMarketRepository

    def __init__(self):
        super().__init__()
        self.producto_repo = ProductoRepository()
        self.detalle_repo = DetalleVentaRepository()

    @transaction.atomic
    def registrar_venta_con_stock(self, venta_data, detalles_data):
        
        #Crear la venta principal
        venta = self.repository.create(**venta_data)
        
        total_venta = 0

        #Procesar cada producto del detalle
        for item in detalles_data:
            producto = self.producto_repo.get_by_id(item['producto_id'])
            cantidad = item['cantidad']

            # Validar si hay stock suficiente
            if producto.stock_actual < cantidad:
                raise ValueError(f"Stock insuficiente para el producto: {producto.nombre}")

            # Calcular subtotal y acumular total
            subtotal = producto.precio_unitario * cantidad
            total_venta += subtotal

            #Crear el detalle de venta
            self.detalle_repo.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_unitario,
                subtotal=subtotal
            )

            #Actualizar stock del producto (Control de stock)
            nuevo_stock = producto.stock_actual - cantidad
            self.producto_repo.update(producto.id, stock_actual=nuevo_stock)

        #Actualizar el total de la venta
        self.repository.update(venta.id, total=total_venta)
        
        return venta

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
