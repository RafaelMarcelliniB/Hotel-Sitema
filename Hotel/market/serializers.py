from rest_framework import serializers

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


class ProductoStockFiltroSerializer(serializers.Serializer):
    stock_bajo = serializers.BooleanField(required=False)


class IngresoMercaderiaCreateSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    precio_compra = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    proveedor = serializers.CharField(max_length=150)


class VentaDetalleInputSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)


class VentaMarketCreateSerializer(serializers.Serializer):
    tipo_venta = serializers.ChoiceField(choices=VentaMarket.TipoVenta.choices)
    checkin_vinculado_id = serializers.IntegerField(required=False, allow_null=True)
    metodo_pago = serializers.ChoiceField(choices=VentaMarket.MetodoPago.choices)
    detalles = VentaDetalleInputSerializer(many=True)

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización del catálogo y ventas del módulo market.
# O - Open/Closed: nuevos serializers se suman sin alterar la base común.
# L - Liskov Substitution: cada serializer hijo funciona como un ModelSerializer estándar.
# I - Interface Segregation: cada entidad de market tiene su propio contrato de API.
# D - Dependency Inversion: la capa web depende de BaseSerializer, no del ORM.
# ════════════════════════════════════════
