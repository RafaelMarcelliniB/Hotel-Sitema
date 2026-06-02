from rest_framework import serializers

from core.base_serializers import BaseSerializer
from hotel.models import CargoAdicional, CheckIn, CheckOut, Habitacion, Huesped, Reserva


class HabitacionSerializer(BaseSerializer):
    class Meta:
        model = Habitacion
        fields = '__all__'


class HuespedSerializer(BaseSerializer):
    class Meta:
        model = Huesped
        fields = '__all__'


class CheckInSerializer(BaseSerializer):
    class Meta:
        model = CheckIn
        fields = '__all__'


class CheckOutSerializer(BaseSerializer):
    class Meta:
        model = CheckOut
        fields = '__all__'


class CargoAdicionalSerializer(BaseSerializer):
    class Meta:
        model = CargoAdicional
        fields = '__all__'


class ReservaSerializer(BaseSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'


class HabitacionEstadoSerializer(serializers.Serializer):
    estado_ocupacion = serializers.ChoiceField(choices=Habitacion.EstadoOcupacion.choices, required=False)
    estado_limpieza = serializers.ChoiceField(choices=Habitacion.EstadoLimpieza.choices, required=False)


class CheckInCreateSerializer(serializers.Serializer):
    habitacion_id = serializers.IntegerField()
    huesped_id = serializers.IntegerField(required=False, allow_null=True)
    huesped = serializers.DictField(required=False)
    turno_ingreso = serializers.ChoiceField(choices=CheckIn.TurnoIngreso.choices)
    tipo_pago = serializers.ChoiceField(choices=CheckIn.TipoPago.choices)
    monto_pagado = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    es_pareja = serializers.BooleanField(required=False, default=False)
    fecha_salida_estimada = serializers.DateField(required=False, allow_null=True)
    hora_salida_estimada = serializers.TimeField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs.get('huesped_id') and not attrs.get('huesped'):
            raise serializers.ValidationError({'huesped': 'Debe enviar huesped_id o huesped para crear el check-in.'})
        return attrs


class CargoAdicionalCreateSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=150)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)


class CheckOutCreateSerializer(serializers.Serializer):
    metodo_pago = serializers.ChoiceField(choices=CheckOut.MetodoPago.choices)


class ReservaLookupSerializer(serializers.Serializer):
    fecha = serializers.DateField(required=False)


class HuespedBusquedaSerializer(serializers.Serializer):
    dni = serializers.CharField(required=False, allow_blank=True)

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de cada entidad del módulo hotel.
# O - Open/Closed: nuevos serializers se agregan sin modificar los existentes.
# L - Liskov Substitution: cada serializer hijo puede reemplazar a la base DRF esperada.
# I - Interface Segregation: cada entidad tiene su propio serializer especializado.
# D - Dependency Inversion: la API depende de BaseSerializer y no de ModelSerializer concreto.
# ════════════════════════════════════════
