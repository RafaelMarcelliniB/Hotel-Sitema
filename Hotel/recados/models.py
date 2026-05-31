from django.conf import settings
from django.db import models

from core.base_models import BaseModel


class Recado(BaseModel):
	class ColorAlerta(models.TextChoices):
		ROJO = 'ROJO', 'Rojo'
		VERDE = 'VERDE', 'Verde'
		AMARILLO = 'AMARILLO', 'Amarillo'
		AZUL = 'AZUL', 'Azul'
		FUCSIA = 'FUCSIA', 'Fucsia'
		BLANCO = 'BLANCO', 'Blanco'

	class Prioridad(models.TextChoices):
		ALTA = 'ALTA', 'Alta'
		MEDIA = 'MEDIA', 'Media'
		BAJA = 'BAJA', 'Baja'

	trabajador_origen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='recados_emitidos')
	turno_origen = models.CharField(max_length=20)
	contenido = models.TextField()
	color_alerta = models.CharField(max_length=20, choices=ColorAlerta.choices)
	personal_a_cargo = models.CharField(max_length=150)
	fecha = models.DateField()
	leido = models.BooleanField(default=False)
	prioridad = models.CharField(max_length=20, choices=Prioridad.choices)

	def __str__(self) -> str:
		return self.contenido[:40]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define los recados y alertas de turno.
# O - Open/Closed: nuevos colores o prioridades se agregan sin romper la estructura.
# L - Liskov Substitution: la entidad respeta el contrato esperado por BaseModel.
# I - Interface Segregation: el recado no mezcla responsabilidades de caja, hotel o market.
# D - Dependency Inversion: las capas superiores dependen de este modelo y no de detalles externos.
# ════════════════════════════════════════
