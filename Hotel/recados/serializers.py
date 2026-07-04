from rest_framework import serializers

from core.base_serializers import BaseSerializer
from recados.models import Recado


class RecadoSerializer(BaseSerializer):
    creado_por = serializers.PrimaryKeyRelatedField(read_only=True)
    creado_por_nombre = serializers.SerializerMethodField()
    creado_por_rol = serializers.SerializerMethodField()
    leido = serializers.SerializerMethodField()

    class Meta:
        model = Recado
        fields = [
            'id',
            'creado_por',
            'creado_por_nombre',
            'creado_por_rol',
            'trabajador_origen',
            'categoria',
            'estado',
            'leido',
            'titulo',
            'descripcion',
            'fecha_creacion',
            'fecha',
            'turno_origen',
            'created_at',
            'updated_at',
            'is_active',
        ]
        extra_kwargs = {
            'trabajador_origen': {'read_only': True},
            'fecha': {'read_only': True},
            'estado': {'required': False},
        }

    def validate(self, attrs):
        if self.instance is None and 'estado' not in attrs:
            attrs['estado'] = Recado.Estado.PENDIENTE
        return attrs

    def get_creado_por_nombre(self, obj):
        user = obj.creado_por or obj.trabajador_origen
        if not user:
            return 'Sistema'
        partes = [getattr(user, 'nombre', None), getattr(user, 'apellido', None)]
        nombre = ' '.join([parte for parte in partes if parte])
        return nombre or getattr(user, 'username', 'Sistema')

    def get_leido(self, obj):
        return obj.estado == Recado.Estado.RESUELTO

    def get_creado_por_rol(self, obj):
        user = obj.creado_por or obj.trabajador_origen
        if not user:
            return 'Sistema'
        if hasattr(user, 'get_rol_display'):
            return user.get_rol_display()
        return getattr(user, 'rol', 'Sin rol') or 'Sin rol'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización del módulo recados.
# O - Open/Closed: nuevos serializers se agregan sin alterar esta base.
# L - Liskov Substitution: el serializer hijo funciona como ModelSerializer estándar.
# I - Interface Segregation: expone una única representación del recado.
# D - Dependency Inversion: la API depende de BaseSerializer y no del ORM.
# ════════════════════════════════════════
