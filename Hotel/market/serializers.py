from core.base_serializers import BaseSerializer
from market.models import Categoria, DetalleVenta, IngresoMercaderia, Producto, VentaMarket


class ProductoSerializer(BaseSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class IngresoMercaderiaSerializer(BaseSerializer):
    class Meta:
        model = IngresoMercaderia
        fields = '__all__'


class VentaMarketSerializer(BaseSerializer):
    class Meta:
        model = VentaMarket
        fields = '__all__'


class DetalleVentaSerializer(BaseSerializer):
    class Meta:
        model = DetalleVenta
        fields = '__all__'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización del catálogo y ventas del módulo market.
# O - Open/Closed: nuevos serializers se suman sin alterar la base común.
# L - Liskov Substitution: cada serializer hijo funciona como un ModelSerializer estándar.
# I - Interface Segregation: cada entidad de market tiene su propio contrato de API.
# D - Dependency Inversion: la capa web depende de BaseSerializer, no del ORM.
# ════════════════════════════════════════
