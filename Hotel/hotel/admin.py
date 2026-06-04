from django.contrib import admin
from .models import Habitacion, Huesped, CheckIn, CheckOut, CargoAdicional, Reserva

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'piso', 'tipo', 'estado_ocupacion', 'estado_limpieza', 'tarifa_dia')
    list_filter = ('piso', 'tipo', 'estado_ocupacion', 'estado_limpieza')
    search_fields = ('numero',)

@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni_pasaporte', 'ciudad_origen', 'nacionalidad')
    search_fields = ('nombre', 'apellido', 'dni_pasaporte')

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('habitacion', 'huesped', 'fecha_entrada', 'turno_ingreso', 'monto_pagado', 'estado')
    list_filter = ('estado', 'turno_ingreso', 'fecha_entrada')

@admin.register(CheckOut)
class CheckOutAdmin(admin.ModelAdmin):
    list_display = ('checkin', 'total_general', 'metodo_pago', 'trabajador_checkout')

admin.site.register(CargoAdicional)
admin.site.register(Reserva)