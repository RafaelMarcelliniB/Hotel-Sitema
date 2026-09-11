from django.conf import settings
from django.db import models

from core.base_models import BaseModel


class Categoria(models.TextChoices):
	SNACK = 'SNACK', 'Snack'
	BEBIDA = 'BEBIDA', 'Bebida'
	ALCOHOL = 'ALCOHOL', 'Bebida alcohólica'
	HIGIENE = 'HIGIENE', 'Higiene'
	CHICLE = 'CHICLE', 'Chicle'
	CARAMELO = 'CARAMELO', 'Caramelo'
	GALLETA = 'GALLETA', 'Galleta'
	PRESERVATIVO = 'PRESERVATIVO', 'Preservativo'
	CUBIERTOS = 'CUBIERTOS', 'Cubiertos'
	VASITOS = 'VASITOS', 'Vasitos'


class UbicacionStock(models.TextChoices):
	ALMACEN = 'ALMACEN', 'Almacén'
	RECEPCION = 'RECEPCION', 'Recepción'
	REFRIGERADORA = 'REFRIGERADORA', 'Refrigeradora'


class Producto(BaseModel):
	nombre = models.CharField(max_length=150)
	categoria = models.CharField(max_length=30, choices=Categoria.choices)
	precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
	stock_almacen = models.PositiveIntegerField(default=0)
	stock_recepcion = models.PositiveIntegerField(default=0)
	stock_refrigeradora = models.PositiveIntegerField(default=0)
	stock_minimo = models.PositiveIntegerField(default=0)
	activo = models.BooleanField(default=True)

	@property
	def stock_total(self):
		return self.stock_almacen + self.stock_recepcion + self.stock_refrigeradora

	def __str__(self) -> str:
		return self.nombre


class IngresoMercaderia(BaseModel):
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ingresos')
	cantidad = models.PositiveIntegerField()
	precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
	proveedor = models.CharField(max_length=150)
	fecha = models.DateField()
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ingresos_mercaderia')

	def __str__(self) -> str:
		return f'Ingreso {self.producto}'


class VentaMarket(BaseModel):
	class TipoVenta(models.TextChoices):
		DIRECTO = 'DIRECTO', 'Directo'
		CARGADO_HABITACION = 'CARGADO_HABITACION', 'Cargado a habitación'

	class MetodoPago(models.TextChoices):
		EFECTIVO = 'EFECTIVO', 'Efectivo'
		YAPE = 'YAPE', 'Yape'
		TARJETA = 'TARJETA', 'Tarjeta'

	tipo_venta = models.CharField(max_length=30, choices=TipoVenta.choices)
	checkin_vinculado = models.ForeignKey('hotel.CheckIn', null=True, blank=True, on_delete=models.SET_NULL, related_name='ventas_market')
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ventas_market')
	fecha = models.DateField()
	hora = models.TimeField()
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)

	def __str__(self) -> str:
		return f'Venta {self.id}'


class DetalleVenta(BaseModel):
	venta = models.ForeignKey(VentaMarket, on_delete=models.CASCADE, related_name='detalles')
	producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
	ubicacion_stock = models.CharField(max_length=20, choices=UbicacionStock.choices)
	cantidad = models.PositiveIntegerField()
	precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
	subtotal = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self) -> str:
		return f'{self.producto} x {self.cantidad}'


class StockTransfer(BaseModel):
	producto = models.ForeignKey(
		Producto, on_delete=models.PROTECT, related_name='transferencias'
	)
	origen = models.CharField(max_length=20, choices=UbicacionStock.choices)
	destino = models.CharField(max_length=20, choices=UbicacionStock.choices)
	cantidad = models.PositiveIntegerField()
	trabajador = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='transferencias_realizadas'
	)
	motivo = models.CharField(max_length=200, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self) -> str:
		return f'Transferencia {self.id}: {self.producto.nombre} {self.get_origen_display()}→{self.get_destino_display()} {self.cantidad}'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define solo catálogo, ingresos y ventas del módulo market.
# O - Open/Closed: nuevas reglas de producto o venta se agregan con nuevos campos o clases.
# L - Liskov Substitution: cada entidad mantiene el contrato de modelo Django y de BaseModel.
# I - Interface Segregation: producto, ingreso y venta están separados por responsabilidad.
# D - Dependency Inversion: servicios y vistas dependen de estas entidades, no de QuerySets sueltos.
# ════════════════════════════════════════
