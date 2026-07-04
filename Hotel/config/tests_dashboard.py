"""
Tests para validar la implementación del CORTE DE CAJA (MÓDULO 1)
Pruebas de filtrado por caja activa en DashboardView
"""

from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from caja.models import Caja, MovimientoCaja

User = get_user_model()


class CortesCajaTestCase(APITestCase):
    """Test suite para validar el filtrado por caja activa"""

    def setUp(self):
        """Crear usuarios y cajas para las pruebas"""
        # Crear Admin
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            nombre='Admin',
            apellido='Sistema',
            rol='admin'
        )
        
        # Crear Cajero 1
        self.cajero1 = User.objects.create_user(
            username='cajero1',
            password='pass123',
            nombre='Juan',
            apellido='Perez',
            rol='cajero'
        )
        
        # Crear Cajero 2
        self.cajero2 = User.objects.create_user(
            username='cajero2',
            password='pass123',
            nombre='Maria',
            apellido='Lopez',
            rol='cajero'
        )
        
        # Crear Recepcionista
        self.recepcionista = User.objects.create_user(
            username='recepcionista',
            password='pass123',
            nombre='Carlos',
            apellido='Ruiz',
            rol='recepcionista'
        )
        
        self.client = APIClient()
        self.hoy = timezone.localdate()
        
    def test_admin_ve_todos_movimientos_del_dia(self):
        """
        CASO 1: Admin debe ver ingresos de TODAS las cajas
        
        Escenario:
        - Cajero 1 abre caja → agrega $100
        - Cajero 2 abre caja → agrega $200
        - Admin consulta dashboard
        
        Esperado: Admin ve "total": 300
        """
        # Abrir caja para Cajero 1
        caja1 = Caja.objects.create(
            trabajador=self.cajero1,
            turno='mañana',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('0'),
            estado='ABIERTA'
        )
        
        # Abrir caja para Cajero 2
        caja2 = Caja.objects.create(
            trabajador=self.cajero2,
            turno='mañana',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('0'),
            estado='ABIERTA'
        )
        
        # Agregar movimiento a caja 1: $100
        MovimientoCaja.objects.create(
            caja=caja1,
            trabajador=self.cajero1,
            turno='mañana',
            tipo='INGRESO',
            tipo_caja='EFECTIVO',
            modulo='HOTEL',
            monto=Decimal('100'),
            referencia='Reserva #001'
        )
        
        # Agregar movimiento a caja 2: $200
        MovimientoCaja.objects.create(
            caja=caja2,
            trabajador=self.cajero2,
            turno='mañana',
            tipo='INGRESO',
            tipo_caja='EFECTIVO',
            modulo='MARKET',
            monto=Decimal('200'),
            referencia='Venta #002'
        )
        
        # Login como Admin y consultar dashboard
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/api/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Admin debe ver el TOTAL de ambas cajas
        expected_total = Decimal('300')
        self.assertEqual(
            data['ingresos_hoy']['total'],
            float(expected_total),
            "Admin debe ver $300 (suma de todas las cajas)"
        )

    def test_cajero_con_caja_abierta_ve_solo_su_caja(self):
        """
        CASO 2: Cajero con caja abierta ve SOLO su dinero
        
        Escenario:
        - Cajero 1 abre caja → agrega $100
        - Cajero 2 abre caja → agrega $200
        - Cajero 1 consulta dashboard
        
        Esperado: Cajero 1 ve "total": 100
        """
        # Abrir caja para Cajero 1
        caja1 = Caja.objects.create(
            trabajador=self.cajero1,
            turno='mañana',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('0'),
            estado='ABIERTA'
        )
        
        # Abrir caja para Cajero 2
        caja2 = Caja.objects.create(
            trabajador=self.cajero2,
            turno='mañana',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('0'),
            estado='ABIERTA'
        )
        
        # Agregar $100 a caja 1
        MovimientoCaja.objects.create(
            caja=caja1,
            trabajador=self.cajero1,
            turno='mañana',
            tipo='INGRESO',
            tipo_caja='EFECTIVO',
            modulo='HOTEL',
            monto=Decimal('100'),
            referencia='Pago #001'
        )
        
        # Agregar $200 a caja 2
        MovimientoCaja.objects.create(
            caja=caja2,
            trabajador=self.cajero2,
            turno='mañana',
            tipo='INGRESO',
            tipo_caja='EFECTIVO',
            modulo='HOTEL',
            monto=Decimal('200'),
            referencia='Pago #002'
        )
        
        # Login como Cajero 1 y consultar
        self.client.login(username='cajero1', password='pass123')
        response = self.client.get('/api/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Cajero 1 debe ver SOLO sus $100
        self.assertEqual(
            data['ingresos_hoy']['total'],
            float(Decimal('100')),
            "Cajero 1 debe ver solo $100 (su caja)"
        )

    def test_empleado_sin_caja_abierta_ve_ceros(self):
        """
        CASO 3: 🔒 CORTE DE CAJA - Empleado sin caja ve $0 en todo
        
        Escenario:
        - Cajero 1 cierra su caja (estado='CERRADA')
        - Hay movimientos históricos en su caja cerrada
        - Cajero 1 consulta dashboard
        
        Esperado: Dashboard muestra "total": 0, "efectivo": 0, etc.
        """
        # Crear caja cerrada (turno anterior)
        caja_cerrada = Caja.objects.create(
            trabajador=self.cajero1,
            turno='noche',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('50'),
            estado='CERRADA',  # ← CERRADA
            monto_final=Decimal('350'),
            fecha_cierre=self.hoy,
            hora_cierre=timezone.now().time()
        )
        
        # Agregar movimientos históricos a esa caja cerrada
        MovimientoCaja.objects.create(
            caja=caja_cerrada,
            trabajador=self.cajero1,
            turno='noche',
            tipo='INGRESO',
            tipo_caja='EFECTIVO',
            modulo='HOTEL',
            monto=Decimal('300'),
            referencia='Turno anterior'
        )
        
        # Login como Cajero 1 (sin caja abierta) y consultar
        self.client.login(username='cajero1', password='pass123')
        response = self.client.get('/api/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Dashboard debe mostrar $0 en todas las métricas
        self.assertEqual(
            data['ingresos_hoy']['total'],
            0.0,
            "Empleado sin caja abierta debe ver $0 en total"
        )
        self.assertEqual(
            data['ingresos_hoy']['hotel'],
            0.0,
            "Debe ver $0 en Hotel"
        )
        self.assertEqual(
            data['ingresos_hoy']['market'],
            0.0,
            "Debe ver $0 en Market"
        )
        self.assertEqual(
            data['grafico_pagos']['efectivo'],
            0.0,
            "Debe ver $0 en Efectivo"
        )

    def test_recepcionista_con_caja_activa_ve_su_dinero(self):
        """
        CASO 4: Recepcionista (también empleado) ve su caja
        
        Verifica que la lógica funciona para RECEPCIONISTA también
        """
        # Abrir caja para Recepcionista
        caja = Caja.objects.create(
            trabajador=self.recepcionista,
            turno='tarde',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('0'),
            estado='ABIERTA'
        )
        
        # Agregar movimiento
        MovimientoCaja.objects.create(
            caja=caja,
            trabajador=self.recepcionista,
            turno='tarde',
            tipo='INGRESO',
            tipo_caja='YAPE',
            modulo='HOTEL',
            monto=Decimal('150'),
            referencia='Adelanto Reserva'
        )
        
        # Login y consultar
        self.client.login(username='recepcionista', password='pass123')
        response = self.client.get('/api/dashboard/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Recepcionista debe ver sus $150
        self.assertEqual(
            data['ingresos_hoy']['total'],
            150.0,
            "Recepcionista debe ver $150"
        )


class MetricasFinancierasTestCase(APITestCase):
    """Tests específicos para métricas de efectivo, yape, tarjeta"""

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='pass123',
            nombre='Admin',
            apellido='Prueba',
            rol='admin'
        )
        self.cajero = User.objects.create_user(
            username='cajero',
            password='pass123',
            nombre='Cajero',
            apellido='Prueba',
            rol='cajero'
        )
        self.client = APIClient()
        self.hoy = timezone.localdate()

    def test_desglose_metodos_pago_empleado(self):
        """
        Verifica que un empleado solo ve sus métodos de pago
        
        Caja con: $100 efectivo + $50 yape + $30 tarjeta
        """
        caja = Caja.objects.create(
            trabajador=self.cajero,
            turno='mañana',
            fecha_apertura=self.hoy,
            hora_apertura=timezone.now().time(),
            monto_inicial=Decimal('0'),
            estado='ABIERTA'
        )
        
        # $100 efectivo
        MovimientoCaja.objects.create(
            caja=caja, trabajador=self.cajero, turno='mañana',
            tipo='INGRESO', tipo_caja='EFECTIVO', modulo='HOTEL',
            monto=Decimal('100')
        )
        
        # $50 yape
        MovimientoCaja.objects.create(
            caja=caja, trabajador=self.cajero, turno='mañana',
            tipo='INGRESO', tipo_caja='YAPE', modulo='MARKET',
            monto=Decimal('50')
        )
        
        # $30 tarjeta
        MovimientoCaja.objects.create(
            caja=caja, trabajador=self.cajero, turno='mañana',
            tipo='INGRESO', tipo_caja='TARJETA', modulo='HOTEL',
            monto=Decimal('30')
        )
        
        self.client.login(username='cajero', password='pass123')
        response = self.client.get('/api/dashboard/')
        data = response.json()
        
        self.assertEqual(
            data['grafico_pagos']['efectivo'],
            100.0
        )
        self.assertEqual(
            data['grafico_pagos']['yape'],
            50.0
        )
        self.assertEqual(
            data['grafico_pagos']['tarjeta'],
            30.0
        )
        self.assertEqual(
            data['ingresos_hoy']['total'],
            180.0
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
