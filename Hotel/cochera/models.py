from django.conf import settings
from django.db import models

from core.base_models import BaseModel


class EspacioCochera(BaseModel):
	class Tipo(models.TextChoices):
		AUTO = 'AUTO', 'Auto'
		MOTO = 'MOTO', 'Moto'
		BUS = 'BUS', 'Bus'

	class Estado(models.TextChoices):
		LIBRE = 'LIBRE', 'Libre'
		OCUPADO = 'OCUPADO', 'Ocupado'

	numero = models.CharField(max_length=20, unique=True)
	tipo = models.CharField(max_length=10, choices=Tipo.choices)
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.LIBRE)

	def __str__(self) -> str:
		return f'Espacio {self.numero}'


class RegistroVehiculo(BaseModel):
	class TipoCliente(models.TextChoices):
		PUBLICO = 'PUBLICO', 'Público'
		HUESPED = 'HUESPED', 'Huésped'

	class TarifaTipo(models.TextChoices):
		POR_HORA = 'POR_HORA', 'Por hora'
		FRACCION = 'FRACCION', 'Fracción'
		DIA_COMPLETO = 'DIA_COMPLETO', 'Día completo'
		NOCTURNA = 'NOCTURNA', 'Nocturna'

	placa = models.CharField(max_length=20)
	tipo_vehiculo = models.CharField(max_length=50)
	marca = models.CharField(max_length=50)
	color = models.CharField(max_length=50)
	nombre_conductor = models.CharField(max_length=150)
	dni_conductor = models.CharField(max_length=30)
	telefono = models.CharField(max_length=30, blank=True)
	tipo_cliente = models.CharField(max_length=20, choices=TipoCliente.choices)
	checkin_vinculado = models.ForeignKey('hotel.CheckIn', null=True, blank=True, on_delete=models.SET_NULL, related_name='vehiculos')
	fecha_entrada = models.DateField()
	hora_entrada = models.TimeField()
	fecha_salida = models.DateField(null=True, blank=True)
	hora_salida = models.TimeField(null=True, blank=True)
	hora_salida_estimada = models.CharField(max_length=50, blank=True)
	observaciones = models.TextField(blank=True)
	tarifa_tipo = models.CharField(max_length=20, choices=TarifaTipo.choices)
	monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	espacio = models.ForeignKey(EspacioCochera, on_delete=models.PROTECT, related_name='vehiculos')
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='vehiculos_registrados')

	def __str__(self) -> str:
		return self.placa

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define espacios y registros de vehículos de cochera.
# O - Open/Closed: nuevos tipos o estados se agregan sin reescribir la capa base.
# L - Liskov Substitution: ambas entidades respetan el contrato de BaseModel y Django.
# I - Interface Segregation: el espacio y el registro vehicular se modelan por separado.
# D - Dependency Inversion: las capas superiores dependen de estas abstracciones del dominio.
# ════════════════════════════════════════
