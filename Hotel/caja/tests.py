from datetime import date, time
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.test import TestCase
from openpyxl import load_workbook
from rest_framework.test import APIClient
from rest_framework import status

from caja.models import Caja, MovimientoCaja
from caja.views import CajaResumenView, ReportesVentasExcelView
from hotel.models import CheckIn, Habitacion, Huesped


class CajaResumenDashboardTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='dashboard-test', password='secret123', nombre='Test', apellido='User')
        self.client = APIClient()
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

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/caja/resumen/', {'periodo': 'hoy'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('total_deudas', response.data['consolidado'])
        self.assertEqual(response.data['consolidado']['total_ingresos'], 70.0)
        self.assertEqual(response.data['consolidado']['total_egresos'], 10.0)
        self.assertEqual(response.data['consolidado']['total_general'], 60.0)
        self.assertEqual(response.data['desglose_pago']['efectivo'], 50.0)
        self.assertEqual(response.data['desglose_pago']['yape'], 20.0)
        self.assertEqual(response.data['desglose_pago']['tarjeta'], 0.0)

    def test_reporte_personalizado_incluye_dni_y_datos_huesped_en_excel(self):
        habitacion = Habitacion.objects.create(
            numero='101',
            piso=1,
            tipo=Habitacion.Tipo.DOBLE,
            marca_tv=Habitacion.MarcaTV.JVC,
            tipo_cama=Habitacion.TipoCama.DOS_PLAZAS,
            tarifa_dia=Decimal('100.00'),
            tarifa_noche=Decimal('90.00'),
            tarifa_madrugada=Decimal('80.00'),
        )
        huesped = Huesped.objects.create(
            nombre='Juan',
            apellido='Pérez',
            dni_pasaporte='12345678',
            telefono='999999999',
            ciudad_origen='Lima',
            nacionalidad=Huesped.Nacionalidad.PERU,
            estado_civil=Huesped.EstadoCivil.SOLTERO,
            tipo_visita=Huesped.TipoVisita.INDEPENDIENTE,
        )
        checkin = CheckIn.objects.create(
            habitacion=habitacion,
            huesped=huesped,
            trabajador=self.user,
            fecha_entrada=date.today(),
            hora_entrada=time(12, 0),
            turno_ingreso=CheckIn.TurnoIngreso.DIA,
            tipo_pago=CheckIn.TipoPago.EFECTIVO,
            monto_pagado=Decimal('50.00'),
            estado=CheckIn.Estado.ACTIVO,
        )
        MovimientoCaja.objects.create(
            caja=self.caja,
            trabajador=self.user,
            turno=self.caja.turno,
            tipo=MovimientoCaja.Tipo.INGRESO,
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
            modulo=MovimientoCaja.Modulo.HOTEL,
            monto=Decimal('50.00'),
            referencia=f'Pago Adelantado Check-in #{checkin.id}',
            descripcion=f'Pago Adelantado Hab #{habitacion.numero} - Huésped: {huesped.nombre} {huesped.apellido}',
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/reportes/ventas-excel/', {
            'trabajador_id': self.user.id,
            'periodo': 'personalizado',
            'fecha_inicio': date.today().isoformat(),
            'fecha_fin': date.today().isoformat(),
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        workbook = load_workbook(filename=BytesIO(response.content))
        sheet = workbook.active
        headers = [cell.value for cell in sheet[1]]
        self.assertIn('DNI', headers)
        self.assertIn('Nombre Huésped', headers)
        self.assertIn('Apellido Huésped', headers)

        row_values = [cell.value for cell in sheet[2]]
        dni_index = headers.index('DNI')
        nombre_index = headers.index('Nombre Huésped')
        apellido_index = headers.index('Apellido Huésped')
        self.assertEqual(row_values[dni_index], '12345678')
        self.assertEqual(row_values[nombre_index], 'Juan')
        self.assertEqual(row_values[apellido_index], 'Pérez')
