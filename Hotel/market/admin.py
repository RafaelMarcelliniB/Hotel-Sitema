from django.contrib import admin
from .models import Producto, IngresoMercaderia, VentaMarket, DetalleVenta

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_unitario', 'stock_actual', 'tipo_registro', 'activo')
    list_filter = ('categoria', 'tipo_registro', 'activo')
    search_fields = ('nombre',)

@admin.register(VentaMarket)
class VentaMarketAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_venta', 'trabajador', 'fecha', 'total', 'metodo_pago')
    list_filter = ('tipo_venta', 'metodo_pago', 'fecha')

admin.site.register(IngresoMercaderia)
admin.site.register(DetalleVenta)