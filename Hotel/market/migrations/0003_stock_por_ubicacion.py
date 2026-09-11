from django.db import migrations, models


def distribuir_stock_existente(apps, schema_editor):
    Producto = apps.get_model('market', 'Producto')
    Producto.objects.filter(stock_actual__gt=0).update(
        stock_almacen=models.F('stock_actual'),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('market', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='stock_almacen',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='producto',
            name='stock_recepcion',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='producto',
            name='stock_refrigeradora',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='detalleventa',
            name='ubicacion_stock',
            field=models.CharField(default='ALMACEN', max_length=20),
        ),
        migrations.RunPython(distribuir_stock_existente, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='detalleventa',
            name='ubicacion_stock',
            field=models.CharField(choices=[('ALMACEN', 'Almacén'), ('RECEPCION', 'Recepción'), ('REFRIGERADORA', 'Refrigeradora')], max_length=20),
        ),
    ]