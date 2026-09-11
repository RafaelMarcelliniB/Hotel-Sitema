from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from core.base_services import BaseService
from caja.models import Caja, MovimientoCaja
from caja.repositories import CajaRepository, MovimientoCajaRepository


class CajaService(BaseService):
    repository_class = CajaRepository

    @transaction.atomic
    def abrir_caja(self, datos, trabajador):
        turno = datos['turno']
        if self.repository.model.objects.filter(estado=Caja.Estado.ABIERTA, turno=turno, trabajador=trabajador).exists():
            raise ValueError('Ya existe una caja abierta para este trabajador en este turno.')
        monto_inicial = datos.get('monto_inicial')
        if monto_inicial is None:
            caja_anterior = self.repository.model.objects.filter(
                trabajador=trabajador,
                fecha_apertura=timezone.localdate(),
                estado=Caja.Estado.CERRADA,
            ).order_by('-fecha_cierre', '-hora_cierre').first()
            monto_inicial = caja_anterior.monto_final if caja_anterior else 0
        return self.repository.create(
            trabajador=trabajador,
            turno=turno,
            fecha_apertura=timezone.localdate(),
            hora_apertura=timezone.localtime().time(),
            monto_inicial=monto_inicial,
            estado=Caja.Estado.ABIERTA,
        )

    @transaction.atomic
    def cerrar_caja(self, caja, datos):
        ingresos_efectivo = caja.movimientos.filter(
            tipo=MovimientoCaja.Tipo.INGRESO,
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
        ).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        egresos_efectivo = caja.movimientos.filter(
            tipo=MovimientoCaja.Tipo.EGRESO,
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
        ).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        monto_esperado = Decimal(caja.monto_inicial) + ingresos_efectivo - egresos_efectivo
        monto_real = datos['monto_real']
        diferencia = monto_real - monto_esperado
        fecha_cierre = timezone.localdate()
        hora_cierre = timezone.localtime().time()
        caja.movimientos.update(
            bloqueado=True,
            trabajador=caja.trabajador,
            turno=caja.turno,
        )

        return self.repository.update(
            caja.id,
            fecha_cierre=fecha_cierre,
            hora_cierre=hora_cierre,
            monto_final=monto_real,
            monto_esperado=monto_esperado,
            monto_real=monto_real,
            diferencia=diferencia,
            notas_cierre=datos.get('notas', ''),
            estado=Caja.Estado.CERRADA,
        )

    def obtener_resumen(self, caja):
        # Capturamos todos los movimientos del turno actual
        movimientos = caja.movimientos.all().order_by('fecha_hora')
        
        # SOLUCIÓN DEL BUG: Filtramos por tipo_caja pero asegurando que SOLO sume el dinero que ingresó realmente
        ingresos_efectivo = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO, 
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto')).get('total') or 0
        egresos_efectivo = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
            tipo=MovimientoCaja.Tipo.EGRESO,
        ).aggregate(total=Sum('monto')).get('total') or 0

        ingresos_yape = movimientos.filter(
            tipo_caja__in=[MovimientoCaja.TipoCaja.YAPE, MovimientoCaja.TipoCaja.PLIN],
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto')).get('total') or 0
        egresos_yape = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.YAPE,
            tipo=MovimientoCaja.Tipo.EGRESO,
        ).aggregate(total=Sum('monto')).get('total') or 0

        ingresos_tarjeta = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.TARJETA, 
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto')).get('total') or 0
        egresos_tarjeta = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.TARJETA,
            tipo=MovimientoCaja.Tipo.EGRESO,
        ).aggregate(total=Sum('monto')).get('total') or 0
        
        total_ingresos = movimientos.filter(tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0
        total_egresos = movimientos.filter(tipo=MovimientoCaja.Tipo.EGRESO).aggregate(total=Sum('monto')).get('total') or 0
        deudas = movimientos.filter(tipo=MovimientoCaja.Tipo.DEUDA, pagada=False)
        
        # OPERACIÓN MATEMÁTICA PURA: Monto Inicial + lo recaudado en los diferentes métodos - salidas efectivas
        efectivo_neto = float(caja.monto_inicial) + float(ingresos_efectivo) - float(egresos_efectivo)
        yape_neto = float(ingresos_yape) - float(egresos_yape)
        tarjeta_neta = float(ingresos_tarjeta) - float(egresos_tarjeta)
        total_general = efectivo_neto + yape_neto + tarjeta_neta
        
        return {
            'monto_inicial': caja.monto_inicial,
            'total_efectivo': efectivo_neto,
            'ingresos_efectivo': ingresos_efectivo,
            'egresos_efectivo': egresos_efectivo,
            'total_yape': yape_neto,
            'ingresos_yape': ingresos_yape,
            'egresos_yape': egresos_yape,
            'total_tarjeta': tarjeta_neta,
            'ingresos_tarjeta': ingresos_tarjeta,
            'egresos_tarjeta': egresos_tarjeta,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'total_general': total_general,  
            'monto_esperado_efectivo': efectivo_neto,
            'deudas_pendientes': deudas,
            'movimientos': movimientos,
        }

    def obtener_deudas_pendientes_activas(self):
        """
        Calcula DEUDAS PENDIENTES únicamente desde CheckIn activos.
        
        Lógica:
        - Una deuda "pendiente" solo existe si el CheckIn está en estado ACTIVO
        - Una vez que se completa el CheckOut, el CheckIn cambia a CERRADO
        - Las deudas finalizadas no deben contarse en el Dashboard
        
        Devuelve: Suma total de monto_deuda de todos los CheckIn activos
        """
        from hotel.models import CheckIn
        
        checkins_activos = CheckIn.objects.filter(estado=CheckIn.Estado.ACTIVO)
        total_deudas = checkins_activos.aggregate(total=Sum('monto_deuda')).get('total') or 0
        
        return float(total_deudas)


class MovimientoCajaService(BaseService):
    repository_class = MovimientoCajaRepository

    @transaction.atomic
    def agregar_movimiento(self, datos, caja):
        if caja.estado == Caja.Estado.CERRADA:
            raise ValueError('No se puede agregar movimientos a una caja cerrada.')

        return self.repository.create(
            caja=caja,
            trabajador=caja.trabajador,
            turno=caja.turno,
            bloqueado=False,
            **datos
        )

    @transaction.atomic
    def pagar_deuda(self, movimiento):
        movimiento.pagada = True
        movimiento.save(update_fields=['pagada'])
        return movimiento

    @transaction.atomic
    def registrar_egreso(self, datos, caja, trabajador):
        return self.agregar_movimiento({
            'tipo': MovimientoCaja.Tipo.EGRESO,
            'tipo_caja': datos['tipo_caja'],
            'modulo': MovimientoCaja.Modulo.OTRO,
            'referencia': datos['categoria'],
            'monto': datos['monto'],
            'descripcion': datos['descripcion'],
        }, caja)

    @transaction.atomic
    def ajustar_tarifa(self, datos, caja, trabajador):
        from hotel.models import CheckIn
        from users.models import AuditLog

        checkin = CheckIn.objects.select_for_update().select_related('habitacion', 'huesped').get(pk=datos['checkin_id'])
        monto = Decimal(str(datos['monto']))
        es_reembolso = datos['accion'] == 'REEMBOLSO'
        if es_reembolso:
            checkin.monto_pagado = max(checkin.monto_pagado - monto, Decimal('0'))
        else:
            checkin.monto_deuda += monto
        checkin.save(update_fields=['monto_pagado', 'monto_deuda'])

        movimiento = self.agregar_movimiento({
            'tipo': MovimientoCaja.Tipo.EGRESO if es_reembolso else MovimientoCaja.Tipo.INGRESO,
            'tipo_caja': datos['tipo_caja'],
            'modulo': MovimientoCaja.Modulo.HOTEL,
            'referencia': f'REEMBOLSO / CORRECCIÓN DE TARIFA - CheckIn #{checkin.id}',
            'monto': monto,
            'descripcion': datos['motivo'],
        }, caja)
        AuditLog.objects.create(
            trabajador=trabajador,
            accion='ajuste_tarifa',
            modulo='caja',
            detalle=f'{movimiento.referencia}; usuario={trabajador}; monto={monto}; motivo={datos["motivo"]}',
        )
        return movimiento

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio de caja.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos sustituyen a BaseService sin romper.
# I - Interface Segregation: cada servicio cubre una sola responsabilidad concreta.
# D - Dependency Inversion: la vista depende de servicios y no del ORM.
# ════════════════════════════════════════
