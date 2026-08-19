from decimal import Decimal

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
    monto_inicial = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False)
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


class EgresoInputSerializer(serializers.Serializer):
    categoria = serializers.ChoiceField(choices=[
        ('SERVICIOS', 'Servicios'),
        ('INSUMOS_LIMPIEZA', 'Insumos/Limpieza'),
        ('COMPRAS_MARKET', 'Compras Market'),
        ('DEVOLUCION', 'Devolución'),
        ('GASTOS_VARIOS', 'Gastos Varios'),
    ])
    descripcion = serializers.CharField(required=True, allow_blank=False)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    tipo_caja = serializers.ChoiceField(choices=[
        (MovimientoCaja.TipoCaja.EFECTIVO, 'Efectivo'),
        (MovimientoCaja.TipoCaja.YAPE, 'Yape'),
    ])


class AjusteTarifaInputSerializer(serializers.Serializer):
    checkin_id = serializers.IntegerField(min_value=1)
    accion = serializers.ChoiceField(choices=['REEMBOLSO', 'COBRO_ADICIONAL'])
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    motivo = serializers.CharField(required=True, allow_blank=False)
    tipo_caja = serializers.ChoiceField(choices=MovimientoCaja.TipoCaja.choices, default=MovimientoCaja.TipoCaja.EFECTIVO)

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de caja y sus movimientos.
# O - Open/Closed: nuevos serializers se añaden sin modificar la base.
# L - Liskov Substitution: cada serializer hijo funciona como ModelSerializer estándar.
# I - Interface Segregation: apertura/cierre y movimiento están separados.
# D - Dependency Inversion: la API depende de BaseSerializer y no del ORM.
# ════════════════════════════════════════
