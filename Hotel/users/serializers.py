from rest_framework import serializers

from core.base_serializers import BaseSerializer
from users.models import AuditLog, Trabajador


class TrabajadorSerializer(BaseSerializer):
    class Meta:
        model = Trabajador
        fields = [
            'id',
            'username',
            'nombre',
            'apellido',
            'rol',
            'turno',
            'activo',
            'is_staff',
            'is_superuser',
            'last_login',
            'date_joined',
        ]


class TrabajadorWriteSerializer(BaseSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = Trabajador
        fields = [
            'id',
            'username',
            'nombre',
            'apellido',
            'rol',
            'turno',
            'activo',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        trabajador = Trabajador(**validated_data)
        if password:
            trabajador.set_password(password)
        trabajador.save()
        return trabajador

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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
