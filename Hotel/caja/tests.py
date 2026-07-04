from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status

from caja.models import Caja, MovimientoCaja
from caja.views import CajaResumenView


class CajaResumenDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard-test', password='secret123')
        self.caja = Caja.objects.create(
            trabajador=self.user,
            turno=Caja.Turno.MANANA,
            fecha_apertura=date.today(),
            hora_apertura=time(10, 0),
            monto_inicial=Decimal('100.00'),
            estado=Caja.Estado.ABIERTA,
        )

    def test_resumen_excluye_deudas_del_consolidado_y_desglose(self):
        MovimientoCaja.objects.create(
            caja=self.caja,
            trabajador=self.user,
            turno=self.caja.turno,
            tipo=MovimientoCaja.Tipo.INGRESO,
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
            modulo=MovimientoCaja.Modulo.HOTEL,
            monto=Decimal('50.00'),
            descripcion='Ingreso efectivo',
        )
        MovimientoCaja.objects.create(
            caja=self.caja,
            trabajador=self.user,
            turno=self.caja.turno,
            tipo=MovimientoCaja.Tipo.INGRESO,
            tipo_caja=MovimientoCaja.TipoCaja.YAPE,
            modulo=MovimientoCaja.Modulo.MARKET,
            monto=Decimal('20.00'),
            descripcion='Ingreso yape',
        )
        MovimientoCaja.objects.create(
            caja=self.caja,
            trabajador=self.user,
            turno=self.caja.turno,
            tipo=MovimientoCaja.Tipo.DEUDA,
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
            modulo=MovimientoCaja.Modulo.HOTEL,
            monto=Decimal('200.00'),
            descripcion='Deuda pendiente',
        )
        MovimientoCaja.objects.create(
            caja=self.caja,
            trabajador=self.user,
            turno=self.caja.turno,
            tipo=MovimientoCaja.Tipo.EGRESO,
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
            modulo=MovimientoCaja.Modulo.OTRO,
            monto=Decimal('10.00'),
            descripcion='Egreso',
        )

        factory = APIRequestFactory()
        request = factory.get('/caja/resumen/', {'periodo': 'hoy'})
        request.user = self.user

        response = CajaResumenView.as_view()(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('total_deudas', response.data['consolidado'])
        self.assertEqual(response.data['consolidado']['total_ingresos'], 70.0)
        self.assertEqual(response.data['consolidado']['total_egresos'], 10.0)
        self.assertEqual(response.data['consolidado']['total_general'], 160.0)
        self.assertEqual(response.data['desglose_pago']['efectivo'], 50.0)
        self.assertEqual(response.data['desglose_pago']['yape'], 20.0)
        self.assertEqual(response.data['desglose_pago']['tarjeta'], 0.0)
