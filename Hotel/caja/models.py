from django.conf import settings
from django.db import models

from core.base_models import BaseModel


class Caja(BaseModel):
	class Turno(models.TextChoices):
		MANANA = 'mañana', 'Mañana'
		TARDE = 'tarde', 'Tarde'
		NOCHE = 'noche', 'Noche'
		MADRUGADA = 'madrugada', 'Madrugada'

	class Estado(models.TextChoices):
		ABIERTA = 'ABIERTA', 'Abierta'
		CERRADA = 'CERRADA', 'Cerrada'

	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cajas')
	turno = models.CharField(max_length=20, choices=Turno.choices)
	fecha_apertura = models.DateField()
	hora_apertura = models.TimeField()
	monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	fecha_cierre = models.DateField(null=True, blank=True)
	hora_cierre = models.TimeField(null=True, blank=True)
	monto_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTA)

	def __str__(self) -> str:
		return f'Caja {self.trabajador} {self.turno}'


class MovimientoCaja(BaseModel):
	class Tipo(models.TextChoices):
		INGRESO = 'INGRESO', 'Ingreso'
		EGRESO = 'EGRESO', 'Egreso'
		DEUDA = 'DEUDA', 'Deuda'

	class TipoCaja(models.TextChoices):
		EFECTIVO = 'EFECTIVO', 'Efectivo'
		YAPE = 'YAPE', 'Yape'
		TARJETA = 'TARJETA', 'Tarjeta'

	class Modulo(models.TextChoices):
		HOTEL = 'HOTEL', 'Hotel'
		MARKET = 'MARKET', 'Market'
		COCHERA = 'COCHERA', 'Cochera'
		ADICIONAL = 'ADICIONAL', 'Adicional'
		OTRO = 'OTRO', 'Otro'

	caja = models.ForeignKey(Caja, on_delete=models.CASCADE, related_name='movimientos')
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	tipo_caja = models.CharField(max_length=20, choices=TipoCaja.choices)
	modulo = models.CharField(max_length=20, choices=Modulo.choices)
	referencia = models.CharField(max_length=150, blank=True)
	monto = models.DecimalField(max_digits=10, decimal_places=2)
	descripcion = models.TextField(blank=True)
	fecha_hora = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f'{self.tipo} {self.monto}'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la caja y sus movimientos de dinero.
# O - Open/Closed: nuevos tipos de movimiento pueden agregarse sin tocar la base abstracta.
# L - Liskov Substitution: Caja y MovimientoCaja respetan el contrato de modelo base.
# I - Interface Segregation: apertura/cierre y movimiento de caja se mantienen separados.
# D - Dependency Inversion: las reglas de negocio consumirán estas entidades y no SQL directo.
# ════════════════════════════════════════
