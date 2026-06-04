from django.contrib import admin
from .models import Recado

@admin.register(Recado)
class RecadoAdmin(admin.ModelAdmin):
    list_display = ('trabajador_origen', 'prioridad', 'color_alerta', 'fecha', 'leido')
    list_filter = ('prioridad', 'color_alerta', 'leido', 'fecha')
    search_fields = ('contenido', 'personal_a_cargo')