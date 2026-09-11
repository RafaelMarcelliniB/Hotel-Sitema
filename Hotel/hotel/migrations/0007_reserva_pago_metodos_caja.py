from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0006_habitacion_mantenimiento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserva',
            name='tipo_pago_adelanto',
            field=models.CharField(
                choices=[
                    ('EFECTIVO', 'Efectivo'),
                    ('YAPE', 'Yape'),
                    ('PLIN', 'Plin'),
                    ('TRANSFERENCIA', 'Transferencia'),
                    ('TARJETA', 'Tarjeta'),
                ],
                max_length=20,
            ),
        ),
    ]