from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('caja', '0005_alter_movimientocaja_turno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movimientocaja',
            name='tipo_caja',
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
