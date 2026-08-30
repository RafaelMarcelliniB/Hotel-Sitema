from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from hotel.models import Habitacion, Huesped, Reserva, CheckIn
from cochera.models import RegistroVehiculo, EspacioCochera
from cochera.services import RegistroVehiculoService
from hotel.views import _serializar_detalle_checkin


class ReservaApiTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='recepcionista',
            password='secret123',
            nombre='Ana',
            apellido='García',
            rol='recepcionista',
        )

        self.habitacion = Habitacion.objects.create(
            numero='201',
            piso=2,
            tipo=Habitacion.Tipo.DOBLE,
            marca_tv=Habitacion.MarcaTV.HISENSE,
            tipo_cama=Habitacion.TipoCama.QUEEN,
            tarifa_dia=120,
            tarifa_noche=90,
            tarifa_madrugada=70,
            estado_ocupacion=Habitacion.EstadoOcupacion.RESERVADO,
        )

        self.huesped = Huesped.objects.create(
            nombre='Carlos',
            apellido='Poma',
            dni_pasaporte='12345678',
            telefono='999111222',
            ciudad_origen='Lima',
            nacionalidad=Huesped.Nacionalidad.PERU,
            estado_civil=Huesped.EstadoCivil.SOLTERO,
            tipo_visita=Huesped.TipoVisita.TURISTA,
        )

        self.reserva = Reserva.objects.create(
            huesped=self.huesped,
            habitacion_preferida=self.habitacion,
            trabajador=self.user,
            fecha_llegada_estimada=date.today(),
            hora_llegada_estimada=time(14, 0),
            monto_adelanto=20,
            tipo_pago_adelanto=Reserva.TipoPagoAdelanto.EFECTIVO,
            estado=Reserva.Estado.PENDIENTE,
        )

    def test_list_reservas_por_habitacion_no_500(self):
        client = APIClient()
        client.force_authenticate(user=self.user)

        response = client.get('/api/hotel/reservas/', {'habitacion_id': self.habitacion.id, 'estado': 'PENDIENTE'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.reserva.id)

    def test_vehiculo_de_huesped_no_cobra_cochera_en_checkout(self):
        espacio = EspacioCochera.objects.create(numero='A1', tipo=EspacioCochera.Tipo.AUTO, estado=EspacioCochera.Estado.OCUPADO)
        checkin = CheckIn.objects.create(
            habitacion=self.habitacion,
            huesped=self.huesped,
            trabajador=self.user,
            fecha_entrada=date.today(),
            hora_entrada='10:00:00',
            turno_ingreso=CheckIn.TurnoIngreso.DIA,
            tipo_pago=CheckIn.TipoPago.EFECTIVO,
            estado=CheckIn.Estado.ACTIVO,
        )
        vehiculo = RegistroVehiculo.objects.create(
            placa='ABC123',
            tipo_vehiculo='AUTO',
            marca='Toyota',
            color='Negro',
            nombre_conductor='Elvin Castro',
            dni_conductor='12345678',
            telefono='999999999',
            tipo_cliente=RegistroVehiculo.TipoCliente.HUESPED,
            checkin_vinculado=checkin,
            fecha_entrada=date.today(),
            hora_entrada='10:30:00',
            tarifa_tipo=RegistroVehiculo.TarifaTipo.POR_HORA,
            monto_total=5.00,
            espacio=espacio,
            trabajador=self.user,
        )

        detalle = _serializar_detalle_checkin(checkin)

        self.assertEqual(len(detalle['vehiculos_cochera']), 1)
        self.assertEqual(detalle['vehiculos_cochera'][0]['monto_total'], 0.0)
        self.assertEqual(RegistroVehiculoService().calcular_monto_para_registro(vehiculo.id), 0)
