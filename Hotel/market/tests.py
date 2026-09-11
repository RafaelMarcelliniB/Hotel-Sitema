import csv
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from market.models import Producto


class StockTransferAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='admin-stock',
            password='pass123',
            rol='admin',
            nombre='Admin',
            apellido='Stock',
        )
        self.client.force_authenticate(user=self.user)

    def test_transferir_desde_almacen_a_recepcion_actualiza_stock(self):
        producto = Producto.objects.create(
            nombre='Agua Mineral',
            categoria='BEBIDA',
            precio_unitario=2.50,
            stock_almacen=20,
            stock_recepcion=3,
            stock_refrigeradora=4,
        )

        response = self.client.post(
            f'/api/market/productos/{producto.id}/transferir/',
            {
                'origen': 'ALMACEN',
                'destino': 'RECEPCION',
                'cantidad': 5,
                'motivo': 'Reposición de recepción',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        producto.refresh_from_db()
        self.assertEqual(producto.stock_almacen, 15)
        self.assertEqual(producto.stock_recepcion, 8)
        self.assertEqual(producto.stock_refrigeradora, 4)

    def test_descargar_plantilla_usa_columnas_actualizadas(self):
        response = self.client.get('/api/market/productos/plantilla/csv/')

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8-sig')
        self.assertIn('Nombre,Categoria,Precio Unitario,Stock Almacen,Stock Recepcion,Stock Refrigeradora,Stock Minimo,Activo', content.splitlines()[0])
        self.assertIn('Agua Mineral,BEBIDA,4.5,15,0,0,5,SI', content)

    def test_importar_csv_con_columnas_actualizadas_crea_producto(self):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(['Nombre', 'Categoria', 'Precio Unitario', 'Stock Almacen', 'Stock Recepcion', 'Stock Refrigeradora', 'Stock Minimo', 'Activo'])
        writer.writerow(['Galleta Oreo', 'GALLETA', '6.50', '10', '2', '0', '5', 'true'])

        response = self.client.post(
            '/api/market/productos/importar-excel/',
            {'file': SimpleUploadedFile('productos.csv', csv_buffer.getvalue().encode('utf-8'), content_type='text/csv')},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(Producto.objects.filter(nombre='Galleta Oreo').count(), 1)
        self.assertEqual(response.json()['created'], 1)

    def test_importar_csv_legacy_stock_actual_sigue_funcionando(self):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(['Nombre', 'Categoria', 'Precio Unitario', 'Stock Actual', 'Stock Minimo', 'Tipo Registro', 'Activo'])
        writer.writerow(['Botella Agua', 'BEBIDA', '4.00', '12', '3', 'Stock', 'SI'])

        response = self.client.post(
            '/api/market/productos/importar-excel/',
            {'file': SimpleUploadedFile('legacy_productos.csv', csv_buffer.getvalue().encode('utf-8'), content_type='text/csv')},
            format='multipart',
        )

        self.assertEqual(response.status_code, 200, response.content)
        producto = Producto.objects.get(nombre='Botella Agua')
        self.assertEqual(producto.stock_almacen, 12)
        self.assertEqual(producto.stock_recepcion, 0)
        self.assertEqual(producto.stock_refrigeradora, 0)
        self.assertTrue(producto.activo)
