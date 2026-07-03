from django.contrib import admin

from .models import Recado


@admin.register(Recado)
class RecadoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'estado', 'creado_por', 'fecha_creacion')
    list_filter = ('categoria', 'estado', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion', 'creado_por__username')