from django.conf import settings
from django.db import migrations, models


def populate_movimiento_trabajador_turno(apps, schema_editor):
    MovimientoCaja = apps.get_model('caja', 'MovimientoCaja')
    for movimiento in MovimientoCaja.objects.select_related('caja').all():
        movimiento.trabajador_id = movimiento.caja.trabajador_id
        movimiento.turno = movimiento.caja.turno
        movimiento.save(update_fields=['trabajador_id', 'turno'])


class Migration(migrations.Migration):
    dependencies = [
        ('caja', '0003_movimientocaja_pagada'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='movimientocaja',
            name='bloqueado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='movimientocaja',
            name='trabajador',
            field=models.ForeignKey(
                null=True,
                on_delete=models.PROTECT,
                related_name='movimientos_caja',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='movimientocaja',
            name='turno',
            field=models.CharField(
                choices=[
                    ('mañana', 'Mañana'),
                    ('tarde', 'Tarde'),
                    ('noche', 'Noche'),
                    ('madrugada', 'Madrugada'),
                ],
                default='mañana',
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_movimiento_trabajador_turno, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='movimientocaja',
            name='trabajador',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='movimientos_caja',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
