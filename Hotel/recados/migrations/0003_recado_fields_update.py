from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recados', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='recado',
            name='categoria',
            field=models.CharField(choices=[('MARKET', 'Market'), ('MANTENIMIENTO', 'Mantenimiento'), ('LIMPIEZA', 'Limpieza'), ('GENERAL', 'General')], default='GENERAL', max_length=20),
        ),
        migrations.AddField(
            model_name='recado',
            name='creado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recados_creados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recado',
            name='descripcion',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='recado',
            name='estado',
            field=models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('PROCESO', 'En Proceso'), ('RESUELTO', 'Resuelto')], default='PENDIENTE', max_length=20),
        ),
        migrations.AddField(
            model_name='recado',
            name='fecha_creacion',
            field=models.DateField(auto_now_add=True, default='2026-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recado',
            name='titulo',
            field=models.CharField(default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='recado',
            name='contenido',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='recado',
            name='fecha',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recado',
            name='trabajador_origen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='recados_emitidos', to=settings.AUTH_USER_MODEL),
        ),
    ]
