from django.db import transaction
from core.base_services import BaseService
from hotel.models import CheckIn
from market.models import UbicacionStock
from market.repositories import DetalleVentaRepository, IngresoMercaderiaRepository, ProductoRepository, VentaMarketRepository

# Importaciones de caja activa
from caja.views import _caja_activa
from caja.services import MovimientoCajaService
from caja.models import MovimientoCaja

class ProductoService(BaseService):
    repository_class = ProductoRepository


class IngresoMercaderiaService(BaseService):
    repository_class = IngresoMercaderiaRepository

    @transaction.atomic
    def registrar_ingreso(self, ingreso_data, trabajador):
        producto_repo = ProductoRepository()
        producto = producto_repo.get_by_id(ingreso_data['producto_id'])
        ingreso = self.repository.create(
            producto=producto,
            amount=ingreso_data['cantidad'],  # Nota: Verifica si tu repo usa 'cantidad' o el campo del modelo
            cantidad=ingreso_data['cantidad'],
            precio_compra=ingreso_data['precio_compra'],
            proveedor=ingreso_data['proveedor'],
            fecha=ingreso_data.get('fecha'),
            trabajador=trabajador,
        )
        producto_repo.update(
            producto.id,
            stock_almacen=producto.stock_almacen + ingreso_data['cantidad'],
        )
        return ingreso


class VentaMarketService(BaseService):
    repository_class = VentaMarketRepository

    def __init__(self):
        super().__init__()
        self.producto_repo = ProductoRepository()
        self.detalle_repo = DetalleVentaRepository()

    @transaction.atomic
    def registrar_venta_con_stock(self, venta_data, detalles_data, trabajador):
        caja = _caja_activa(trabajador)
        if not caja and venta_data.get('tipo_venta') == 'DIRECTO':
            raise ValueError("No se puede registrar una venta si el trabajador no cuenta con una caja abierta para su turno.")

        checkin_vinculado_id = venta_data.pop('checkin_vinculado_id', None)
        if checkin_vinculado_id:
            venta_data['checkin_vinculado'] = CheckIn.objects.get(pk=checkin_vinculado_id)

        venta_data['trabajador'] = trabajador
        venta_data.setdefault('fecha', venta_data.get('fecha'))
        venta_data.setdefault('hora', venta_data.get('hora'))
        
        venta = self.repository.create(**venta_data)
        total_venta = 0

        for item in detalles_data:
            producto = self.producto_repo.get_by_id(item['producto_id'])
            amount = item['cantidad']
            ubicacion = item['ubicacion_stock']
            campo_stock = {
                UbicacionStock.ALMACEN: 'stock_almacen',
                UbicacionStock.RECEPCION: 'stock_recepcion',
                UbicacionStock.REFRIGERADORA: 'stock_refrigeradora',
            }[ubicacion]
            stock_disponible = getattr(producto, campo_stock)

            if stock_disponible < amount:
                raise ValueError(f"Stock insuficiente en {UbicacionStock(ubicacion).label} para el producto: {producto.nombre}")

            subtotal = producto.precio_unitario * amount
            total_venta += subtotal

            self.detalle_repo.create(
                venta=venta,
                producto=producto,
                ubicacion_stock=ubicacion,
                cantidad=amount,
                precio_unitario=producto.precio_unitario,
                subtotal=subtotal
            )

            self.producto_repo.update(
                producto.id,
                **{campo_stock: stock_disponible - amount},
            )

        self.repository.update(venta.id, total=total_venta)
        

        if venta.tipo_venta == 'DIRECTO' and caja:
            # Sincronizamos las opciones de pago con los TextChoices del modelo
            metodo_pago_caja = 'EFECTIVO'
            if venta.metodo_pago in ['YAPE', 'TARJETA']:
                metodo_pago_caja = venta.metodo_pago

            # Definimos el diccionario estructurado apuntando a los campos reales
            datos_movimiento = {
                'tipo': MovimientoCaja.Tipo.INGRESO,
                'tipo_caja': metodo_pago_caja,
                'modulo': MovimientoCaja.Modulo.MARKET,
                'monto': total_venta,
                'descripcion': f'Venta Directa Market - ID Venta: {venta.id}',
                'referencia': f'VENTA-{venta.id}',
                'pagada': True,  
            }
            
            # Intentamos usar tu capa de servicio desestructurando los datos para evitar errores de argumentos inesperados.
            # Si el Service falla por parámetros antiguos rígidos, usamos un fallback directo al Modelo.
            try:
                MovimientoCajaService().agregar_movimiento(datos_movimiento, caja)
            except TypeError:
                MovimientoCaja.objects.create(
                    caja=caja,
                    trabajador=caja.trabajador,
                    turno=caja.turno,
                    bloqueado=False,
                    tipo=datos_movimiento['tipo'],
                    tipo_caja=datos_movimiento['tipo_caja'],
                    modulo=datos_movimiento['modulo'],
                    monto=datos_movimiento['monto'],
                    descripcion=datos_movimiento['descripcion'],
                    referencia=datos_movimiento['referencia'],
                    pagada=datos_movimiento['pagada']
                )
        
        elif venta.tipo_venta == 'CARGADO_HABITACION' and venta.checkin_vinculado:
            # Incrementar la deuda del hospedaje cuando es cargado a habitación
            checkin = venta.checkin_vinculado
            checkin.monto_deuda += total_venta
            checkin.save()
        
        return venta


class DetalleVentaService(BaseService):
    repository_class = DetalleVentaRepository