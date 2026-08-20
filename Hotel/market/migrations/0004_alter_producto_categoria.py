from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0003_stock_por_ubicacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='categoria',
            field=models.CharField(
                choices=[
                    ('SNACK', 'Snack'),
                    ('BEBIDA', 'Bebida'),
                    ('ALCOHOL', 'Bebida alcohólica'),
                    ('HIGIENE', 'Higiene'),
                    ('CHICLE', 'Chicle'),
                    ('CARAMELO', 'Caramelo'),
                    ('GALLETA', 'Galleta'),
                    ('PRESERVATIVO', 'Preservativo'),
                    ('CUBIERTOS', 'Cubiertos'),
                    ('VASITOS', 'Vasitos'),
                ],
                max_length=30,
            ),
        ),
    ]
