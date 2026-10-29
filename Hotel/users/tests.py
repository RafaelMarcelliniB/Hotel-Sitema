from rest_framework.test import APITestCase

from users.models import Trabajador

LOGIN = '/api/users/auth/login/'
ME = '/api/users/auth/me/'


class TrabajadorInactivoTests(APITestCase):
    def setUp(self):
        self.admin = Trabajador.objects.create_user(
            username='adm', password='pw12345!', nombre='A', apellido='D',
            rol='admin', is_superuser=True, is_staff=True,
        )
        self.cajero = Trabajador.objects.create_user(
            username='caj', password='pw12345!', nombre='C', apellido='J', rol='cajero',
        )

    def _token(self, username):
        resp = self.client.post(LOGIN, {'username': username, 'password': 'pw12345!'})
        self.assertEqual(resp.status_code, 200)
        return resp.data['access']

    def _toggle(self, trabajador):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self._token('adm'))
        resp = self.client.patch(f'/api/users/trabajadores/{trabajador.pk}/toggle-activo/')
        self.client.credentials()
        return resp

    def test_inactivo_no_puede_iniciar_sesion(self):
        self.assertEqual(self._toggle(self.cajero).status_code, 200)
        resp = self.client.post(LOGIN, {'username': 'caj', 'password': 'pw12345!'})
        self.assertEqual(resp.status_code, 401)

    def test_token_vigente_deja_de_servir_al_desactivar(self):
        token = self._token('caj')
        self._toggle(self.cajero)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        self.assertEqual(self.client.get(ME).status_code, 401)

    def test_reactivar_restituye_el_acceso(self):
        self._toggle(self.cajero)
        self._toggle(self.cajero)
        self.assertEqual(self.client.post(LOGIN, {'username': 'caj', 'password': 'pw12345!'}).status_code, 200)

    def test_usuario_creado_inactivo_no_entra(self):
        Trabajador.objects.create_user(
            username='ina', password='pw12345!', nombre='I', apellido='N', rol='cajero', activo=False,
        )
        self.assertEqual(self.client.post(LOGIN, {'username': 'ina', 'password': 'pw12345!'}).status_code, 401)

    def test_admin_no_puede_desactivarse_a_si_mismo(self):
        self.assertEqual(self._toggle(self.admin).status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.activo)
