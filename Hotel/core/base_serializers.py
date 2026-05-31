from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: centraliza la base común para serializers de API.
# O - Open/Closed: nuevos serializers heredan esta base sin modificarla.
# L - Liskov Substitution: cualquier serializer hijo puede usarse donde se espera un ModelSerializer.
# I - Interface Segregation: no fuerza campos ni reglas de validación específicas de módulos.
# D - Dependency Inversion: las capas superiores dependen de esta abstracción y no de implementaciones concretas.
# ════════════════════════════════════════
