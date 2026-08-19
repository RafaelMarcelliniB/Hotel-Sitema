from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0007_reserva_pago_metodos_caja'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkin',
            name='tipo_pago',
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