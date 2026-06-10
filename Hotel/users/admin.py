from django.contrib import admin
from users.models import AuditLog, Trabajador

@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('username', 'nombre', 'apellido', 'rol', 'turno', 'activo', 'is_superuser')
    search_fields = ('username', 'nombre', 'apellido')
    list_filter = ('rol', 'turno', 'activo')
    
    # Esto permite que al hacer clic en el usuario puedas editar
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'email')}),
        ('Atributos de Hotel', {'fields': ('rol', 'turno', 'activo')}),
        ('Permisos Especiales', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    def save_model(self, request, obj, form, change):
        """Aseguramos que si el admin escribe una contraseña en texto plano, se guarde hasheada."""
        pwd = form.cleaned_data.get('password')
        if pwd:
            # Si el password ingresado no parece ser un hash, asumimos texto plano
            low = str(pwd)
            if not (low.startswith('pbkdf2_') or low.startswith('argon2$') or low.startswith('bcrypt$')):
                obj.set_password(pwd)
        super().save_model(request, obj, form, change)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'accion', 'modulo', 'fecha_hora', 'ip')
    search_fields = ('accion', 'modulo', 'detalle')
    list_filter = ('modulo', 'fecha_hora')