from django.contrib import admin
from .models import Caja, MovimientoCaja

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'turno', 'fecha_apertura', 'monto_inicial', 'monto_final', 'estado')
    list_filter = ('estado', 'turno', 'fecha_apertura')
    search_fields = ('trabajador__username',)

@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ('caja', 'tipo', 'tipo_caja', 'modulo', 'monto', 'fecha_hora', 'pagada')
    list_filter = ('tipo', 'tipo_caja', 'modulo', 'pagada')
    search_fields = ('referencia', 'descripcion')