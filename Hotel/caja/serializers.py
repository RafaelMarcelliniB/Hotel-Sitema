from rest_framework import serializers

from core.base_serializers import BaseSerializer
from caja.models import Caja, MovimientoCaja


class CajaSerializer(BaseSerializer):
    class Meta:
        model = Caja
        fields = '__all__'


class MovimientoCajaSerializer(BaseSerializer):
    class Meta:
        model = MovimientoCaja
        fields = '__all__'


class CajaAperturaSerializer(serializers.Serializer):
    monto_inicial = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    turno = serializers.ChoiceField(choices=Caja.Turno.choices)


class CajaCierreSerializer(serializers.Serializer):
    pass


class MovimientoCajaInputSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=MovimientoCaja.Tipo.choices)
    tipo_caja = serializers.ChoiceField(choices=MovimientoCaja.TipoCaja.choices)
    modulo = serializers.ChoiceField(choices=MovimientoCaja.Modulo.choices)
    referencia = serializers.CharField(max_length=150, required=False, allow_blank=True)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    descripcion = serializers.CharField(required=False, allow_blank=True)

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de caja y sus movimientos.
# O - Open/Closed: nuevos serializers se añaden sin modificar la base.
# L - Liskov Substitution: cada serializer hijo funciona como ModelSerializer estándar.
# I - Interface Segregation: apertura/cierre y movimiento están separados.
# D - Dependency Inversion: la API depende de BaseSerializer y no del ORM.
# ════════════════════════════════════════
