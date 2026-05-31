from django.contrib import admin

from users.models import AuditLog, Trabajador


@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
	list_display = ('username', 'nombre', 'apellido', 'rol', 'turno', 'activo')
	search_fields = ('username', 'nombre', 'apellido')
	list_filter = ('rol', 'turno', 'activo')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ('trabajador', 'accion', 'modulo', 'fecha_hora', 'ip')
	search_fields = ('accion', 'modulo', 'detalle')
	list_filter = ('modulo', 'fecha_hora')

# Register your models here.
