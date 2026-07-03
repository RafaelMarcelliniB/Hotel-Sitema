from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from core.base_services import BaseService
from users.models import AuditLog
from hotel.models import CargoAdicional, CheckIn, Habitacion
from hotel.repositories import CargoAdicionalRepository, CheckInRepository, CheckOutRepository, HabitacionRepository, HuespedRepository, ReservaRepository

# IMPORTACIONES AÑADIDAS: Necesarias para interactuar con el saldo del dashboard y la caja activa
from caja.models import Caja, MovimientoCaja
from cochera.models import RegistroVehiculo


class HabitacionService(BaseService):
    repository_class = HabitacionRepository

    def cambiar_estado(self, habitacion_id, datos):
        return self.repository.update(habitacion_id, **datos)


class HuespedService(BaseService):
    repository_class = HuespedRepository

    def buscar_por_dni(self, dni):
        return self.repository.model.objects.filter(dni_pasaporte=dni).first()

    def crear_huesped(self, data):
        return self.repository.create(**data)


class CheckInService(BaseService):
    repository_class = CheckInRepository

    def __init__(self):
        super().__init__()
        self.habitacion_repo = HabitacionRepository()
        self.huesped_repo = HuespedRepository()

    def _tarifa_habitacion(self, habitacion, turno_ingreso):
        if turno_ingreso == CheckIn.TurnoIngreso.DIA:
            return habitacion.tarifa_dia
        if turno_ingreso == CheckIn.TurnoIngreso.NOCHE:
            return habitacion.tarifa_noche
        return habitacion.tarifa_madrugada

    def _obtener_huesped(self, data):
        huesped_id = data.pop('huesped_id', None)
        huesped_data = data.pop('huesped', None)

        if huesped_id:
            return self.huesped_repo.get_by_id(huesped_id)

        if huesped_data:
            dni = huesped_data.get('dni_pasaporte') or huesped_data.get('dni')
            huesped = self.huesped_repo.model.objects.filter(dni_pasaporte=dni).first() if dni else None
            if huesped:
                return huesped
            return self.huesped_repo.create(
                nombre=huesped_data.get('nombre', ''),
                apellido=huesped_data.get('apellido', ''),
                dni_pasaporte=dni,
                telefono=huesped_data.get('telefono', ''),
                ciudad_origen=huesped_data.get('ciudad_origen', ''),
                nacionalidad=huesped_data.get('nacionalidad', HuespedRepository.model.Nacionalidad.PERU),
                estado_civil=huesped_data.get('estado_civil', HuespedRepository.model.EstadoCivil.SOLTERO),
                tipo_visita=huesped_data.get('tipo_visita', HuespedRepository.model.TipoVisita.INDEPENDIENTE),
            )

        raise ValueError('Debe enviar huesped_id o huesped.')

    @transaction.atomic
    def iniciar_alquiler(self, data, trabajador):
        data = dict(data)
        habitacion = self.habitacion_repo.get_by_id(data.get('habitacion_id') or data.get('habitacion'))
        
        if habitacion.estado_ocupacion != Habitacion.EstadoOcupacion.DISPONIBLE:
            raise ValueError("La habitación no está disponible.")

        huesped = self._obtener_huesped(data)
        turno_ingreso = data.get('turno_ingreso')
        monto_pagado = Decimal(str(data.get('monto_pagado', 0)))
        tarifa = Decimal(str(self._tarifa_habitacion(habitacion, turno_ingreso)))
        monto_deuda = max(tarifa - monto_pagado, Decimal('0'))

        # Crea el Check-In
        checkin = self.repository.create(
            habitacion=habitacion,
            huesped=huesped,
            trabajador=trabajador,
            fecha_entrada=timezone.localdate(),
            hora_entrada=timezone.localtime().time(),
            fecha_salida_estimada=data.get('fecha_salida_estimada'),
            hora_salida_estimada=data.get('hora_salida_estimada'),
            turno_ingreso=turno_ingreso,
            tipo_pago=data.get('tipo_pago'),
            monto_pagado=monto_pagado,
            monto_deuda=monto_deuda,
            es_pareja=data.get('es_pareja', False),
        )

        # Actualiza estado de habitación 
        self.habitacion_repo.update(habitacion.id, estado_ocupacion=Habitacion.EstadoOcupacion.OCUPADO)

        # =====================================================================
        # INYECCIÓN AUTOMÁTICA EN CAJA (SOLUCIÓN AL BALANCE DEL DASHBOARD)
        # =====================================================================
        if monto_pagado > 0:
            hoy = timezone.localdate()
            turno_trabajador = getattr(trabajador, 'turno', None)

            filtros_caja = {
                'trabajador': trabajador,
                'estado': Caja.Estado.ABIERTA,
                'fecha_apertura': hoy,
            }
            if turno_trabajador:
                filtros_caja['turno'] = turno_trabajador

            # Buscamos la caja activa con la misma lógica que Navbar/validaciones
            caja_activa = Caja.objects.filter(**filtros_caja).order_by('-fecha_apertura', '-hora_apertura').first()
            if not caja_activa:
                # Fallback controlado: mismo usuario y fecha local por si hubo cambio de turno en perfil
                caja_activa = Caja.objects.filter(
                    trabajador=trabajador,
                    estado=Caja.Estado.ABIERTA,
                    fecha_apertura=hoy,
                ).order_by('-fecha_apertura', '-hora_apertura').first()

            if caja_activa:
                # Mapear el tipo de pago recibido al campo `tipo_caja` del modelo MovimientoCaja
                tipo_pago = data.get('tipo_pago') or data.get('metodo_pago')
                tipo_caja_val = None
                if tipo_pago:
                    tipo_map = {
                        'EFECTIVO': MovimientoCaja.TipoCaja.EFECTIVO,
                        'YAPE': MovimientoCaja.TipoCaja.YAPE,
                        'TARJETA': MovimientoCaja.TipoCaja.TARJETA,
                        'efectivo': MovimientoCaja.TipoCaja.EFECTIVO,
                        'yape': MovimientoCaja.TipoCaja.YAPE,
                        'tarjeta': MovimientoCaja.TipoCaja.TARJETA,
                    }
                    tipo_caja_val = tipo_map.get(tipo_pago, MovimientoCaja.TipoCaja.EFECTIVO)

                MovimientoCaja.objects.create(
                    caja=caja_activa,
                    trabajador=caja_activa.trabajador,
                    turno=caja_activa.turno,
                    bloqueado=False,
                    monto=monto_pagado,
                    tipo=MovimientoCaja.Tipo.INGRESO,
                    tipo_caja=tipo_caja_val or MovimientoCaja.TipoCaja.EFECTIVO,
                    modulo=MovimientoCaja.Modulo.HOTEL,
                    referencia=f'Pago Adelantado Check-in #{checkin.id}',
                    descripcion=f"Pago Adelantado Hab #{habitacion.numero} - Huésped: {huesped.nombre} {huesped.apellido}",
                    pagada=True
                )

        AuditLog.objects.create(
            trabajador=trabajador,
            accion='checkin_creado',
            modulo='hotel',
            detalle=f'Check-in creado en habitación {habitacion.numero}',
        )
        
        return checkin

    def agregar_cargo_adicional(self, checkin, data, trabajador):
        return CargoAdicional.objects.create(
            checkin=checkin,
            concepto=data['concepto'],
            monto=data['monto'],
            fecha=timezone.localdate(),
            hora=timezone.localtime().time(),
            worker=trabajador,
        )

    def obtener_resumen(self, checkin):
        from decimal import Decimal  # Aseguramos la importación
        from cochera.services import RegistroVehiculoService
        cochera_service = RegistroVehiculoService()

        cargos = checkin.cargos_adicionales.all()
        subtotal_adicionales = sum((cargo.monto for cargo in cargos), Decimal('0'))
        subtotal_market = sum((venta.total for venta in checkin.ventas_market.all()), Decimal('0'))
        
        # 🚗 CÁLCULO EN TIEMPO REAL DE COCHERA SIN INCOHERENCIA DE TIPOS:
        subtotal_cochera = Decimal('0')
        for vehiculo in checkin.vehiculos.all():
            if vehiculo.fecha_salida is not None and vehiculo.monto_total is not None:
                subtotal_cochera += Decimal(str(vehiculo.monto_total))
            else:
                try:
                    monto_actual = cochera_service._calcular_monto(
                        vehiculo.tarifa_tipo,
                        vehiculo.fecha_entrada,
                        vehiculo.hora_entrada
                    )
                    subtotal_cochera += Decimal(str(monto_actual))
                except Exception:
                    subtotal_cochera += Decimal(str(vehiculo.monto_total or 0))
        total_general = subtotal_habitacion + subtotal_adicionales + subtotal_market + subtotal_cochera
        
        return {
            'subtotal_habitacion': subtotal_habitacion,
            'subtotal_adicionales': subtotal_adicionales,
            'subtotal_market': subtotal_market,
            'subtotal_cochera': subtotal_cochera,
            'total_general': total_general,
        }

class CheckOutService(BaseService):
    repository_class = CheckOutRepository

    @transaction.atomic
    def finalizar_alquiler(self, checkin_id, checkout_data, trabajador):
        
        checkin_repo = CheckInRepository()
        habitacion_repo = HabitacionRepository()
        
        checkin = checkin_repo.get_by_id(checkin_id)

        checkout = self.repository.create(checkin=checkin, trabajador_checkout=trabajador, **checkout_data)

        # Actualiza Check-In: marca como CERRADO y resetea deuda a 0
        checkin_repo.update(checkin.id, 
                            estado=CheckIn.Estado.CERRADO,
                            monto_deuda=Decimal('0.00'),  # ← CRUCIAL: Resetea deuda a cero
                            fecha_salida_real=timezone.now().date(),
                            hora_salida_real=timezone.now().time())

        # Libera habitación y marcarla para limpieza (Estado SUCIO)
        habitacion_repo.update(checkin.habitacion.id, 
                                estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE,
                                estado_limpieza=Habitacion.EstadoLimpieza.SUCIO)

        AuditLog.objects.create(
            trabajador=trabajador,
            accion='checkout_creado',
            modulo='hotel',
            detalle=f'Check-out cerrado para habitación {checkin.habitacion.numero}',
        )
        return checkout

class CargoAdicionalService(BaseService):
    repository_class = CargoAdicionalRepository


class ReservaService(BaseService):
    repository_class = ReservaRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio del módulo hotel.
# O - Open/Closed: nuevas reglas de negocio se agregan en nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos pueden reemplazar a BaseService.
# I - Interface Segregation: cada caso de uso tiene su propio servicio.
# D - Dependency Inversion: las vistas dependen de servicios y no del ORM.
# ════════════════════════════════════════