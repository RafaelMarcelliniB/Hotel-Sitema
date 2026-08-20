from django.contrib import admin
from .models import Producto, IngresoMercaderia, VentaMarket, DetalleVenta

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'categoria', 'precio_unitario', 'stock_almacen',
        'stock_recepcion', 'stock_refrigeradora', 'stock_total_admin', 'activo',
    )
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)
    fieldsets = (
        ('Datos Generales', {
            'fields': ('nombre', 'categoria', 'precio_unitario', 'activo'),
        }),
        ('Inventario por Ubicación', {
            'fields': ('stock_almacen', 'stock_recepcion', 'stock_refrigeradora', 'stock_minimo'),
        }),
    )

    @admin.display(description='Stock Total', ordering='stock_almacen')
    def stock_total_admin(self, obj):
        return obj.stock_total

@admin.register(VentaMarket)
class VentaMarketAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_venta', 'trabajador', 'fecha', 'total', 'metodo_pago')
    list_filter = ('tipo_venta', 'metodo_pago', 'fecha')

admin.site.register(IngresoMercaderia)
admin.site.register(DetalleVenta)