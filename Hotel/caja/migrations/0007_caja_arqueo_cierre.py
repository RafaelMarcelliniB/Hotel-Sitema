from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caja', '0006_movimientocaja_metodos_pago'),
    ]

    operations = [
        migrations.AddField(
            model_name='caja',
            name='monto_esperado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='caja',
            name='monto_real',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='caja',
            name='diferencia',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='caja',
            name='notas_cierre',
            field=models.TextField(blank=True),
        ),
    ]