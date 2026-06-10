from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from core.base_services import BaseService
from caja.models import Caja, MovimientoCaja
from caja.repositories import CajaRepository, MovimientoCajaRepository


class CajaService(BaseService):
    repository_class = CajaRepository

    @transaction.atomic
    def abrir_caja(self, datos, trabajador):
        turno = datos['turno']
        if self.repository.model.objects.filter(estado=Caja.Estado.ABIERTA, turno=turno).exists():
            raise ValueError('Ya existe una caja abierta para este turno.')
        return self.repository.create(
            trabajador=trabajador,
            turno=turno,
            fecha_apertura=timezone.localdate(),
            hora_apertura=timezone.localtime().time(),
            monto_inicial=datos['monto_inicial'],
            estado=Caja.Estado.ABIERTA,
        )

    @transaction.atomic
    def cerrar_caja(self, caja):
        # El cierre oficial también debe basarse estrictamente en ingresos y egresos reales
        ingresos = caja.movimientos.filter(tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0
        egresos = caja.movimientos.filter(tipo=MovimientoCaja.Tipo.EGRESO).aggregate(total=Sum('monto')).get('total') or 0
        
        monto_final = float(caja.monto_inicial) + float(ingresos) - float(egresos)
        
        return self.repository.update(
            caja.id,
            fecha_cierre=timezone.localdate(),
            hora_cierre=timezone.localtime().time(),
            monto_final=monto_final,
            estado=Caja.Estado.CERRADA,
        )

    def obtener_resumen(self, caja):
        # Capturamos todos los movimientos del turno actual
        movimientos = caja.movimientos.all().order_by('fecha_hora')
        
        # SOLUCIÓN DEL BUG: Filtramos por tipo_caja pero asegurando que SOLO sume el dinero que ingresó realmente
        total_efectivo = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO, 
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto')).get('total') or 0

        total_yape = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.YAPE, 
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto')).get('total') or 0

        total_tarjeta = movimientos.filter(
            tipo_caja=MovimientoCaja.TipoCaja.TARJETA, 
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto')).get('total') or 0
        
        total_ingresos = movimientos.filter(tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0
        total_egresos = movimientos.filter(tipo=MovimientoCaja.Tipo.EGRESO).aggregate(total=Sum('monto')).get('total') or 0
        deudas = movimientos.filter(tipo=MovimientoCaja.Tipo.DEUDA, pagada=False)
        
        # OPERACIÓN MATEMÁTICA PURA: Monto Inicial + lo recaudado en los diferentes métodos - salidas efectivas
        total_general = float(caja.monto_inicial) + float(total_efectivo) + float(total_yape) + float(total_tarjeta) - float(total_egresos)
        
        return {
            'monto_inicial': caja.monto_inicial,
            'total_efectivo': total_efectivo,
            'total_yape': total_yape,
            'total_tarjeta': total_tarjeta,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'total_general': total_general,  
            'deudas_pendientes': deudas,
            'movimientos': movimientos,
        }


class MovimientoCajaService(BaseService):
    repository_class = MovimientoCajaRepository

    @transaction.atomic
    def agregar_movimiento(self, datos, caja):
        return self.repository.create(caja=caja, **datos)

    @transaction.atomic
    def pagar_deuda(self, movimiento):
        movimiento.pagada = True
        movimiento.save(update_fields=['pagada'])
        return movimiento

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio de caja.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos sustituyen a BaseService sin romper.
# I - Interface Segregation: cada servicio cubre una sola responsabilidad concreta.
# D - Dependency Inversion: la vista depende de servicios y no del ORM.
# ════════════════════════════════════════
