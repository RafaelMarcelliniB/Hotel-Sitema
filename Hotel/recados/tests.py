from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from recados.models import Recado


class RecadoApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='empleado1',
            password='12345678',
            nombre='Ana',
            apellido='García',
        )
        self.client.force_authenticate(self.user)

    def test_create_recado_assigns_authenticated_user(self):
        response = self.client.post(
            '/api/recados/',
            {
                'titulo': 'Falta de stock',
                'categoria': 'MARKET',
                'descripcion': 'Se necesita papel higiénico en recepción.',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['creado_por'], self.user.id)
        self.assertEqual(Recado.objects.get(id=response.data['id']).estado, 'PENDIENTE')

    def test_patch_updates_only_estado(self):
        recado = Recado.objects.create(
            titulo='Mantenimiento de lámpara',
            descripcion='La luz del pasillo falla.',
            categoria='MANTENIMIENTO',
            creado_por=self.user,
            trabajador_origen=self.user,
            fecha=timezone.localdate(),
        )

        response = self.client.patch(
            f'/api/recados/{recado.id}/',
            {'estado': 'PROCESO'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['estado'], 'PROCESO')

        invalid_response = self.client.patch(
            f'/api/recados/{recado.id}/',
            {'estado': 'RESUELTO', 'titulo': 'Cambio de título'},
            format='json',
        )

        self.assertEqual(invalid_response.status_code, 400)
