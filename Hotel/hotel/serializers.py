from rest_framework import serializers

from core.base_serializers import BaseSerializer
from hotel.models import CargoAdicional, CheckIn, CheckOut, Habitacion, Huesped, Reserva


class HabitacionSerializer(BaseSerializer):
    # 1. Campo declarado al nivel principal de la clase
    checkin_actual_id = serializers.SerializerMethodField()

    class Meta:
        model = Habitacion
        fields = [
            'id', 
            'numero', 
            'piso',
            'tipo', 
            'tarifa_dia', 
            'tarifa_noche', 
            'tarifa_madrugada',
            'estado_ocupacion', 
            'estado_limpieza', 
            'checkin_actual_id'
        ]


    def get_checkin_actual_id(self, obj):
        try:
            from hotel.models import CheckIn
            checkin_activo = CheckIn.objects.filter(
                habitacion=obj, 
                estado='ACTIVO'
            ).first()
            
            if checkin_activo:
                return checkin_activo.id
            return None
        except Exception as e:
            print(f"⚠️ Error en serializer: {str(e)}")
            return None
            
class HuespedSerializer(BaseSerializer):
    class Meta:
        model = Huesped
        fields = '__all__'


class CheckInSerializer(BaseSerializer):
    # Declaramos los campos calculados dinámicos que espera el ModalCheckOut.jsx
    huesped = HuespedSerializer(read_only=True)
    monto_habitacion = serializers.SerializerMethodField()
    monto_adicionales = serializers.SerializerMethodField()
    total_pagar = serializers.SerializerMethodField()
    saldo_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        # Traemos todos los campos originales del modelo y acoplamos los calculados
        fields = [
            'id', 'habitacion', 'huesped', 'turno_ingreso', 'tipo_pago', 
            'monto_pagado', 'es_pareja', 'fecha_ingreso', 'hora_ingreso',
            'fecha_salida_estimada', 'hora_salida_estimada', 'estado',
            'monto_habitacion', 'monto_adicionales', 'total_pagar', 'saldo_pendiente'
        ]

    def get_monto_habitacion(self, obj):
        # Si guardas el precio pactado en el check-in usas ese campo, 
        # si no, recurrimos a la tarifa por día de la habitación asociada.
        return float(getattr(obj, 'precio_pactado', getattr(obj.habitacion, 'tarifa_dia', 0.0)))

    def get_monto_adicionales(self, obj):
        try:
            # Buscamos y sumamos todos los cargos adicionales vinculados a este check-in
            from hotel.models import CargoAdicional
            cargos = CargoAdicional.objects.filter(checkin=obj)
            return float(sum(cargo.monto for cargo in cargos))
        except Exception:
            return 0.0

    def get_total_pagar(self, obj):
        # Total acumulado teórico = Costo Habitación + Cargos extras (Market, cochera, etc.)
        costo_hab = self.get_monto_habitacion(obj)
        costo_adi = self.get_monto_adicionales(obj)
        return costo_hab + costo_adi

    def get_saldo_pendiente(self, obj):
        # Saldo Neto = Total acumulado - Lo que ya pagó en el ingreso (adelanto)
        total = self.get_total_pagar(obj)
        adelanto = float(obj.monto_pagado or 0.0)
        saldo = total - adelanto
        return max(0.0, saldo) # Evita que devuelva números negativos si pagó de más


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
