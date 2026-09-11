from django.contrib import admin
from .models import Producto, IngresoMercaderia, VentaMarket, DetalleVenta, StockTransfer


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


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('producto', 'origen', 'destino', 'cantidad', 'trabajador', 'created_at')
    list_filter = ('created_at', 'origen', 'destino')
    search_fields = ('producto__nombre', 'motivo')
    readonly_fields = ('created_at',)


# Admin action for bulk stock transfer
def transferir_stock_action(modeladmin, request, queryset):
    """Bulk action to transfer stock from Almacén to Recepción/Refrigeradora."""
    transferencia_service = StockTransferService()
    
    for producto in queryset:
        # Transfer 50% of almacen stock to recepcion, minimum 1
        stock_almacen = producto.stock_almacen
        if stock_almacen > 0:
            cantidad = max(1, stock_almacen // 2)
            destino = 'RECEPCION'  # Could be configurable
            
            try:
                transferencia_service.transferir_stock(
                    producto_id=producto.id,
                    origen='ALMACEN',
                    destino=destino,
                    cantidad=cantidad,
                    trabajador=request.user,
                    motivo='Transferencia bulk desde admin',
                )
            except ValueError as e:
                # Log or handle insufficient stock, etc.
                pass


transferir_stock_action.short_description = 'Transferir 50% del stock de Almacén a Recepción'


@admin.register(VentaMarket)
class VentaMarketAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_venta', 'trabajador', 'fecha', 'total', 'metodo_pago')
    list_filter = ('tipo_venta', 'metodo_pago', 'fecha')

admin.site.register(IngresoMercaderia)
admin.site.register(DetalleVenta)