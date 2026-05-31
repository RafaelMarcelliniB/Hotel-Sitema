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

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de cada entidad del módulo hotel.
# O - Open/Closed: nuevos serializers se agregan sin modificar los existentes.
# L - Liskov Substitution: cada serializer hijo puede reemplazar a la base DRF esperada.
# I - Interface Segregation: cada entidad tiene su propio serializer especializado.
# D - Dependency Inversion: la API depende de BaseSerializer y no de ModelSerializer concreto.
# ════════════════════════════════════════
