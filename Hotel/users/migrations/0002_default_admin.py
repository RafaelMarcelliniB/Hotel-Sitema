from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_default_admin(apps, schema_editor):
    Trabajador = apps.get_model('users', 'Trabajador')
    admin_user, _ = Trabajador.objects.get_or_create(
        username='admin',
        defaults={
            'nombre': 'Admin',
            'apellido': 'User',
            'rol': 'admin',
            'turno': 'mañana',
            'activo': True,
            'is_staff': True,
            'is_superuser': True,
        },
    )
    admin_user.nombre = 'Admin'
    admin_user.apellido = 'User'
    admin_user.rol = 'admin'
    admin_user.turno = 'mañana'
    admin_user.activo = True
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.password = make_password('admin')
    admin_user.save()


def remove_default_admin(apps, schema_editor):
    apps.get_model('users', 'Trabajador').objects.filter(username='admin').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_admin, remove_default_admin),
    ]
