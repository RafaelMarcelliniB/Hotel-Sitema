from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from caja.models import Caja, MovimientoCaja
from core.base_services import BaseService
from cochera.models import EspacioCochera, RegistroVehiculo
from cochera.repositories import EspacioCocheraRepository, RegistroVehiculoRepository
from hotel.models import CheckIn


class EspacioCocheraService(BaseService):
    repository_class = EspacioCocheraRepository


class RegistroVehiculoService(BaseService):
    repository_class = RegistroVehiculoRepository

    def __init__(self):
        super().__init__()
        self.espacio_repo = EspacioCocheraRepository()

    def _es_cortesia_huesped(self, registro):
        return (
            getattr(registro, 'tipo_cliente', None) == RegistroVehiculo.TipoCliente.HUESPED
            or getattr(registro, 'checkin_vinculado_id', None) is not None
        )

    def _obtener_caja_activa(self, trabajador):
        hoy = timezone.localdate()
        filtros = {
            'trabajador': trabajador,
            'estado': Caja.Estado.ABIERTA,
            'fecha_apertura': hoy,
        }
        turno_usuario = getattr(trabajador, 'turno', None)
        if turno_usuario:
            filtros['turno'] = turno_usuario

        caja = Caja.objects.filter(**filtros).order_by('-fecha_apertura', '-hora_apertura').first()
        if caja:
            return caja

        return Caja.objects.filter(
            trabajador=trabajador,
            estado=Caja.Estado.ABIERTA,
            fecha_apertura=hoy,
        ).order_by('-fecha_apertura', '-hora_apertura').first()

    def _calcular_monto(self, tarifa_tipo, fecha_entrada, hora_entrada):
        ahora = timezone.localtime()
        inicio = timezone.make_aware(timezone.datetime.combine(fecha_entrada, hora_entrada))
        horas = max((ahora - inicio).total_seconds() / 3600, 0)
        tarifas = {
            RegistroVehiculo.TarifaTipo.POR_HORA: 5.0,
            RegistroVehiculo.TarifaTipo.FRACCION: 3.0,
            RegistroVehiculo.TarifaTipo.DIA_COMPLETO: 25.0,
            RegistroVehiculo.TarifaTipo.NOCTURNA: 15.0,
        }
        tarifa_base = tarifas.get(tarifa_tipo, 5.0)
        if tarifa_tipo == RegistroVehiculo.TarifaTipo.DIA_COMPLETO:
            return tarifa_base
        if tarifa_tipo == RegistroVehiculo.TarifaTipo.NOCTURNA:
            return tarifa_base
        if tarifa_tipo == RegistroVehiculo.TarifaTipo.FRACCION:
            return round(((int(horas) + (1 if horas % 1 else 0)) * tarifa_base), 2)
        return round(max(horas, 1) * tarifa_base, 2)

    def calcular_monto_para_registro(self, registro_id):
        registro = RegistroVehiculo.objects.get(pk=registro_id)
        if self._es_cortesia_huesped(registro):
            return Decimal('0')
        return self._calcular_monto(registro.tarifa_tipo, registro.fecha_entrada, registro.hora_entrada)

    @transaction.atomic
    def registrar_ingreso(self, vehiculo_data, trabajador):
        vehiculo_data = dict(vehiculo_data)
        espacio_id = vehiculo_data.pop('espacio_id', None) or vehiculo_data.get('espacio')
        espacio = self.espacio_repo.get_by_id(espacio_id)

        checkin_vinculado_id = vehiculo_data.pop('checkin_vinculado_id', None)
        if checkin_vinculado_id:
            vehiculo_data['checkin_vinculado'] = CheckIn.objects.get(pk=checkin_vinculado_id)

        if espacio.estado != EspacioCochera.Estado.LIBRE:
            raise ValueError(f"El espacio {espacio.numero} ya está ocupado.")

        #Crea el registro de entrada
        monto = Decimal(str(vehiculo_data.pop('monto', 0) or 0))
        detalle_tiempo = vehiculo_data.pop('detalle_tiempo', '').strip()
        es_huesped = bool(vehiculo_data.pop('es_huesped', False))

        if vehiculo_data.get('tipo_cliente') == RegistroVehiculo.TipoCliente.HUESPED:
            monto = Decimal('0')

        vehiculo_data['monto_total'] = monto

        registro = self.repository.create(
            **vehiculo_data,
            espacio=espacio,
            fecha_entrada=timezone.localdate(),
            hora_entrada=timezone.localtime().time(),
            trabajador=trabajador,
        )

        #Actualiza estado del espacio
        self.espacio_repo.update(espacio.id, estado=EspacioCochera.Estado.OCUPADO)

        if monto > 0:
            caja_activa = self._obtener_caja_activa(trabajador)
            if not caja_activa:
                raise ValueError('No existe una caja abierta para registrar el cobro de cochera.')

            MovimientoCaja.objects.create(
                caja=caja_activa,
                trabajador=caja_activa.trabajador,
                turno=caja_activa.turno,
                bloqueado=False,
                tipo=MovimientoCaja.Tipo.INGRESO,
                tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
                modulo=MovimientoCaja.Modulo.COCHERA,
                referencia=registro.placa,
                monto=monto,
                descripcion=f'Ingreso vehículo {registro.placa} - Público General ({detalle_tiempo or "Cobro manual"})',
                pagada=True,
            )
        
        return registro

    @transaction.atomic
    def registrar_salida(self, registro_id):
        # 1. Obtener la instancia real del registro desde el repositorio
        registro = self.repository.get_by_id(registro_id)

        if registro.fecha_salida:
            raise ValueError("Este vehículo ya registró su salida.")

        if self._es_cortesia_huesped(registro):
            monto_calculado = Decimal('0')
        else:
            monto_calculado = registro.monto_total if registro.monto_total and registro.monto_total > 0 else self._calcular_monto(
                registro.tarifa_tipo,
                registro.fecha_entrada,
                registro.hora_entrada,
            )

        try:
            monto_calculado = Decimal(str(monto_calculado))
        except Exception:
            pass

        registro.fecha_salida = timezone.localdate()
        registro.hora_salida = timezone.localtime().time()
        registro.monto_total = monto_calculado
        registro.save()

        if getattr(registro, 'espacio', None):
            self.espacio_repo.update(registro.espacio.id, estado=EspacioCochera.Estado.LIBRE)

        return registro
    
    
# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio de cochera.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos sustituyen a BaseService sin romper.
# I - Interface Segregation: cada servicio cubre una responsabilidad concreta.
# D - Dependency Inversion: la vista depende de servicios, no del ORM.
# ════════════════════════════════════════
