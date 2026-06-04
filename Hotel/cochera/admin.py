from django.contrib import admin
from .models import EspacioCochera, RegistroVehiculo

@admin.register(EspacioCochera)
class EspacioCocheraAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo', 'estado')
    list_filter = ('tipo', 'estado')

@admin.register(RegistroVehiculo)
class RegistroVehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'tipo_vehiculo', 'nombre_conductor', 'tipo_cliente', 'espacio', 'fecha_entrada')
    list_filter = ('tipo_cliente', 'tarifa_tipo', 'fecha_entrada')
    search_fields = ('placa', 'nombre_conductor', 'dni_conductor')