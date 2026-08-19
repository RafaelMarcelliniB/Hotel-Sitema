from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0005_checkin_reserva_alter_reserva_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habitacion',
            name='estado_ocupacion',
            field=models.CharField(
                choices=[
                    ('DISPONIBLE', 'Disponible'),
                    ('OCUPADO', 'Ocupado'),
                    ('RESERVADO', 'Reservado'),
                    ('BLOQUEADO', 'Bloqueado'),
                    ('MANTENIMIENTO', 'Mantenimiento'),
                ],
                default='DISPONIBLE',
                max_length=20,
            ),
        ),
    ]