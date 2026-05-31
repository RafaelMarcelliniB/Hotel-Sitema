from rest_framework import serializers

from core.base_serializers import BaseSerializer
from users.models import AuditLog, Trabajador


class TrabajadorSerializer(BaseSerializer):
    class Meta:
        model = Trabajador
        fields = '__all__'


class AuditLogSerializer(BaseSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la representación API de usuarios y auditoría.
# O - Open/Closed: nuevos campos o serializers del módulo se agregan sin tocar la base común.
# L - Liskov Substitution: los serializers hijos se usan como ModelSerializer estándar.
# I - Interface Segregation: cada recurso expone su propio serializer, sin mezclar responsabilidades.
# D - Dependency Inversion: la capa de API depende de la abstracción BaseSerializer.
# ════════════════════════════════════════
