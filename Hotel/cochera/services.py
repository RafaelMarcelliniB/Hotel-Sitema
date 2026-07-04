from django.db import transaction
from django.utils import timezone

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
        registro = self.repository.create(
            **vehiculo_data,
            espacio=espacio,
            fecha_entrada=timezone.localdate(),
            hora_entrada=timezone.localtime().time(),
            trabajador=trabajador,
        )

        #Actualiza estado del espacio
        self.espacio_repo.update(espacio.id, estado=EspacioCochera.Estado.OCUPADO)
        
        return registro

    @transaction.atomic
    def registrar_salida(self, registro_id):
        # 1. Obtener la instancia real del registro desde el repositorio
        registro = self.repository.get_by_id(registro_id)
        
        if registro.fecha_salida:
            raise ValueError("Este vehículo ya registró su salida.")
        # Calcular el monto usando la lógica de negocio
        monto_calculado = self._calcular_monto(
            registro.tarifa_tipo,
            registro.fecha_entrada,
            registro.hora_entrada,
        )

        # Convertir a Decimal por consistencia
        try:
            from decimal import Decimal
            monto_calculado = Decimal(str(monto_calculado))
        except Exception:
            pass

        # Actualiza la instancia y persiste
        registro.fecha_salida = timezone.localdate()
        registro.hora_salida = timezone.localtime().time()
        registro.monto_total = monto_calculado
        registro.save()

        # Libera el espacio de cochera
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
