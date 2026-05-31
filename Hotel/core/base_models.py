from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define metadatos y campos comunes reutilizables para entidades persistentes.
# O - Open/Closed: nuevos modelos extienden BaseModel sin modificar esta clase base.
# L - Liskov Substitution: cualquier subclase mantiene el contrato de modelo Django esperado.
# I - Interface Segregation: solo expone atributos comunes de persistencia, sin mezclar lógica de negocio.
# D - Dependency Inversion: los modelos concretos dependen de esta abstracción común en lugar de duplicar estructura.
# ════════════════════════════════════════
