from core.base_serializers import BaseSerializer
from cochera.models import EspacioCochera, RegistroVehiculo


class EspacioCocheraSerializer(BaseSerializer):
    class Meta:
        model = EspacioCochera
        fields = '__all__'


class RegistroVehiculoSerializer(BaseSerializer):
    class Meta:
        model = RegistroVehiculo
        fields = '__all__'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de cochera y vehículos.
# O - Open/Closed: nuevos serializers se agregan sin alterar los existentes.
# L - Liskov Substitution: cada serializer hijo es compatible con ModelSerializer.
# I - Interface Segregation: espacio y vehículo tienen su propia representación.
# D - Dependency Inversion: la API depende de la abstracción BaseSerializer.
# ════════════════════════════════════════
