from django.conf import settings
from django.db import models

from core.base_models import BaseModel


class Recado(BaseModel):
    class Categoria(models.TextChoices):
        MARKET = 'MARKET', 'Market'
        MANTENIMIENTO = 'MANTENIMIENTO', 'Mantenimiento'
        LIMPIEZA = 'LIMPIEZA', 'Limpieza'
        GENERAL = 'GENERAL', 'General'

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PROCESO = 'PROCESO', 'En Proceso'
        RESUELTO = 'RESUELTO', 'Resuelto'

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='recados_creados',
        null=True,
        blank=True,
    )
    trabajador_origen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='recados_emitidos',
        null=True,
        blank=True,
    )
    categoria = models.CharField(max_length=20, choices=Categoria.choices, default=Categoria.GENERAL)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    titulo = models.CharField(max_length=120)
    descripcion = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha = models.DateField(null=True, blank=True)
    turno_origen = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        return self.titulo[:40]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define los recados y alertas de turno.
# O - Open/Closed: nuevos colores o prioridades se agregan sin romper la estructura.
# L - Liskov Substitution: la entidad respeta el contrato esperado por BaseModel.
# I - Interface Segregation: el recado no mezcla responsabilidades de caja, hotel o market.
# D - Dependency Inversion: las capas superiores dependen de este modelo y no de detalles externos.
# ════════════════════════════════════════
