from rest_framework import serializers

from core.base_serializers import BaseSerializer
from cochera.models import EspacioCochera, RegistroVehiculo


class EspacioCocheraSerializer(BaseSerializer):
    registro_activo = serializers.SerializerMethodField()

    class Meta:
        model = EspacioCochera
        fields = '__all__'

    def get_registro_activo(self, obj):
        if obj.estado == EspacioCochera.Estado.OCUPADO:
            # Buscamos el último registro que aún no tenga hora de salida
            registro = obj.vehiculos.filter(fecha_salida__isnull=True).last()
            if registro:
                return {
                    "id": registro.id,
                    "placa": registro.placa,
                    "nombre_conductor": registro.nombre_conductor,
                    "dni_conductor": registro.dni_conductor,
                    "hora_entrada": str(registro.hora_entrada),
                    "fecha_entrada": str(registro.fecha_entrada),
                    "tipo_vehiculo": registro.tipo_vehiculo,
                    "habitacion": registro.checkin_vinculado.habitacion.numero if registro.checkin_vinculado else None,
                    "hora_salida_estimada": registro.hora_salida_estimada,
                    "observaciones": registro.observaciones,
                    "tarifa_tipo": registro.tarifa_tipo,
                    "monto_total": str(registro.monto_total),
                    "tipo_cliente": registro.tipo_cliente  # 🔥 Línea agregada para solucionar el bug
                }
        return None


class RegistroVehiculoSerializer(BaseSerializer):
    class Meta:
        model = RegistroVehiculo
        fields = '__all__'


class EspacioCocheraFiltroSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=EspacioCochera.Estado.choices, required=False)


class EspacioCocheraInputSerializer(serializers.Serializer):
    numero = serializers.CharField(max_length=20)
    tipo = serializers.ChoiceField(choices=EspacioCochera.Tipo.choices)
    estado = serializers.ChoiceField(choices=EspacioCochera.Estado.choices, required=False)


class RegistroVehiculoIngresoSerializer(serializers.Serializer):
    placa = serializers.CharField(max_length=20)
    tipo_vehiculo = serializers.CharField(max_length=50)
    marca = serializers.CharField(max_length=50)
    color = serializers.CharField(max_length=50)
    nombre_conductor = serializers.CharField(max_length=150)
    dni_conductor = serializers.CharField(max_length=30)
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    tipo_cliente = serializers.ChoiceField(choices=RegistroVehiculo.TipoCliente.choices)
    checkin_vinculado_id = serializers.IntegerField(required=False, allow_null=True)
    espacio_id = serializers.IntegerField()
    tarifa_tipo = serializers.ChoiceField(choices=RegistroVehiculo.TarifaTipo.choices)
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False, default=0)
    detalle_tiempo = serializers.CharField(max_length=200, required=False, allow_blank=True)
    hora_salida_estimada = serializers.CharField(max_length=50, required=False, allow_blank=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    es_huesped = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        tipo_cliente = attrs.get('tipo_cliente')
        monto = attrs.get('monto', 0)
        checkin_vinculado_id = attrs.get('checkin_vinculado_id')

        if tipo_cliente == RegistroVehiculo.TipoCliente.HUESPED:
            if monto and monto != 0:
                raise serializers.ValidationError('Para huésped el monto debe ser 0.00.')
            if not checkin_vinculado_id:
                raise serializers.ValidationError('Debe vincular un check-in para un huésped.')
        else:
            if monto is None or monto == 0:
                raise serializers.ValidationError('Para público general el monto debe ser mayor a 0.')

        return attrs


class RegistroVehiculoSalidaSerializer(serializers.Serializer):
    pass

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de cochera y vehículos.
# O - Open/Closed: nuevos serializers se agregan sin alterar los existentes.
# L - Liskov Substitution: cada serializer hijo es compatible con ModelSerializer.
# I - Interface Segregation: espacio y vehículo tienen su propia representación.
# D - Dependency Inversion: la API depende de la abstracción BaseSerializer.
# ════════════════════════════════════════
