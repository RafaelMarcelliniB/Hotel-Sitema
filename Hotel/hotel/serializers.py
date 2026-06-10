from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal
from core.base_serializers import BaseSerializer
from hotel.models import CargoAdicional, CheckIn, CheckOut, Habitacion, Huesped, Reserva

class HabitacionSerializer(BaseSerializer):
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
            # Filtramos de manera segura por el estado activo
            checkin_activo = CheckIn.objects.filter(
                habitacion=obj, 
                estado=CheckIn.Estado.ACTIVO
            ).first()
            
            if checkin_activo:
                return checkin_activo.id
            return None
        except Exception as e:
            print(f"⚠️ Error en serializer Habitacion: {str(e)}")
            return None
            
class HuespedSerializer(BaseSerializer):
    class Meta:
        model = Huesped
        fields = '__all__'


class CheckInSerializer(BaseSerializer):
    huesped = HuespedSerializer(read_only=True)
    monto_habitacion = serializers.SerializerMethodField()
    monto_adicionales = serializers.SerializerMethodField()
    total_pagar = serializers.SerializerMethodField()
    saldo_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = CheckIn
        # 🔥 Corregido: Se cambiaron fecha_ingreso/hora_ingreso por fecha_entrada/hora_entrada coincidiendo con tu modelo
        fields = [
            'id', 'habitacion', 'huesped', 'turno_ingreso', 'tipo_pago', 
            'monto_pagado', 'es_pareja', 'fecha_entrada', 'hora_entrada',
            'fecha_salida_estimada', 'hora_salida_estimada', 'estado',
            'monto_habitacion', 'monto_adicionales', 'total_pagar', 'saldo_pendiente'
        ]

    def get_monto_habitacion(self, obj):
        # Aseguramos compatibilidad estricta con string o enum del ChoiceField
        turno = str(obj.turno_ingreso).upper()
        if 'DIA' in turno:
            return float(obj.habitacion.tarifa_dia)
        if 'NOCHE' in turno:
            return float(obj.habitacion.tarifa_noche)
        return float(obj.habitacion.tarifa_madrugada)

    def get_monto_adicionales(self, obj):
        from decimal import Decimal
        from django.db.models import Sum
        from market.models import VentaMarket
        from cochera.models import RegistroVehiculo

        try:
            # 1. Cargos adicionales del hotel
            sub_cargos = obj.cargos_adicionales.aggregate(total=Sum('monto'))['total']
            sub_cargos = Decimal(str(sub_cargos)) if sub_cargos is not None else Decimal('0.00')

            # 2. Ventas del market
            sub_market = VentaMarket.objects.filter(checkin_vinculado=obj).aggregate(total=Sum('total'))['total']
            sub_market = Decimal(str(sub_market)) if sub_market is not None else Decimal('0.00')
            
            # 3. Cochera (Controlamos estrictamente si no hay registros vinculados aún)
            vehiculos_query = RegistroVehiculo.objects.filter(checkin_vinculado=obj)
            if vehiculos_query.exists():
                sub_cochera = vehiculos_query.aggregate(total=Sum('monto_total'))['total']
                sub_cochera = Decimal(str(sub_cochera)) if sub_cochera is not None else Decimal('0.00')
            else:
                sub_cochera = Decimal('0.00')
            
            # Sumamos de forma limpia usando el mismo tipo de dato estricto (Decimal)
            total_calculado = sub_cargos + sub_market + sub_cochera
            return float(total_calculado)

        except Exception as e:
            # Si algo falla de todas formas, devolvemos un float compatible limpio para evitar el Error 500
            print(f"Error interno en get_monto_adicionales: {e}")
            return 0.0

    def get_total_pagar(self, obj):
        return self.get_monto_habitacion(obj) + self.get_monto_adicionales(obj)

    def get_saldo_pendiente(self, obj):
        total = self.get_total_pagar(obj)
        adelanto = float(obj.monto_pagado or 0.0)
        return max(0.0, total - adelanto)


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