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

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización de caja y sus movimientos.
# O - Open/Closed: nuevos serializers se añaden sin modificar la base.
# L - Liskov Substitution: cada serializer hijo funciona como ModelSerializer estándar.
# I - Interface Segregation: apertura/cierre y movimiento están separados.
# D - Dependency Inversion: la API depende de BaseSerializer y no del ORM.
# ════════════════════════════════════════
