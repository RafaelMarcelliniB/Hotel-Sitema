from django.contrib import admin
from .models import Caja, MovimientoCaja

@admin.register(Caja)
class CajaAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'turno', 'fecha_apertura', 'monto_inicial', 'monto_final', 'estado')
    list_filter = ('estado', 'turno', 'fecha_apertura')
    search_fields = ('trabajador__username',)
    list_select_related = ('trabajador',)
    ordering = ('-fecha_apertura', '-hora_apertura')

@admin.register(MovimientoCaja)
class MovimientoCajaAdmin(admin.ModelAdmin):
    list_display = ('caja', 'trabajador', 'turno', 'tipo', 'tipo_caja', 'modulo', 'monto', 'fecha_hora', 'pagada')
    list_filter = ('tipo', 'tipo_caja', 'modulo', 'pagada', 'turno')
    search_fields = ('referencia', 'descripcion', 'trabajador__username', 'caja__trabajador__username')
    list_select_related = ('caja', 'trabajador')
    raw_id_fields = ('caja', 'trabajador')
    ordering = ('-fecha_hora',)
