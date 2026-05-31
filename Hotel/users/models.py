from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from core.base_models import BaseModel


class Trabajador(BaseModel, AbstractUser):
	class Rol(models.TextChoices):
		ADMIN = 'admin', 'Admin'
		RECEPCIONISTA = 'recepcionista', 'Recepcionista'
		CAJERO = 'cajero', 'Cajero'

	class Turno(models.TextChoices):
		MANANA = 'mañana', 'Mañana'
		TARDE = 'tarde', 'Tarde'
		NOCHE = 'noche', 'Noche'
		MADRUGADA = 'madrugada', 'Madrugada'

	nombre = models.CharField(max_length=100)
	apellido = models.CharField(max_length=100)
	rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.RECEPCIONISTA)
	turno = models.CharField(max_length=20, choices=Turno.choices, default=Turno.MANANA)
	activo = models.BooleanField(default=True)
	REQUIRED_FIELDS = ['nombre', 'apellido']

	def __str__(self) -> str:
		return f'{self.nombre} {self.apellido}'


class AuditLog(BaseModel):
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='audit_logs')
	accion = models.CharField(max_length=150)
	modulo = models.CharField(max_length=100)
	fecha_hora = models.DateTimeField(auto_now_add=True)
	detalle = models.TextField(blank=True)
	ip = models.GenericIPAddressField(null=True, blank=True)

	def __str__(self) -> str:
		return f'{self.trabajador} - {self.accion}'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define el modelo de autenticación y el log de auditoría del módulo users.
# O - Open/Closed: nuevos campos o modelos del módulo se agregan sin alterar la base abstracta.
# L - Liskov Substitution: Trabajador y AuditLog respetan el contrato de modelo Django y de BaseModel.
# I - Interface Segregation: la autenticación y la auditoría están separadas en entidades distintas.
# D - Dependency Inversion: las capas superiores consumen esta abstracción de dominio y no lógica dispersa.
# ════════════════════════════════════════

# Create your models here.
