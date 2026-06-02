from decimal import Decimal

from django.db.models import F, Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
from cochera.models import EspacioCochera
from hotel.models import CheckIn, Habitacion, Reserva
from market.models import Producto
from recados.models import Recado


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.localdate()
        habitaciones = Habitacion.objects.all()
        checkins_activos = CheckIn.objects.filter(estado=CheckIn.Estado.ACTIVO).select_related('habitacion', 'huesped')
        reservas_hoy = Reserva.objects.filter(fecha_llegada_estimada=hoy).select_related('huesped', 'habitacion_preferida')
        productos_stock_bajo = Producto.objects.filter(activo=True, stock_actual__lte=F('stock_minimo')).order_by('nombre')
        movimientos_hoy = MovimientoCaja.objects.filter(fecha_hora__date=hoy).order_by('-fecha_hora')
        pagos_hoy = MovimientoCaja.objects.filter(fecha_hora__date=hoy, tipo=MovimientoCaja.Tipo.INGRESO)

        ingresos_hotel = movimientos_hoy.filter(modulo=MovimientoCaja.Modulo.HOTEL, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        ingresos_market = movimientos_hoy.filter(modulo=MovimientoCaja.Modulo.MARKET, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        ingresos_cochera = movimientos_hoy.filter(modulo=MovimientoCaja.Modulo.COCHERA, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        total_ingresos = ingresos_hotel + ingresos_market + ingresos_cochera

        deudas_qs = MovimientoCaja.objects.filter(tipo=MovimientoCaja.Tipo.DEUDA, pagada=False)
        deudas_total = deudas_qs.aggregate(total=Sum('monto')).get('total') or Decimal('0')

        pagos_efectivo = pagos_hoy.filter(tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        pagos_yape = pagos_hoy.filter(tipo_caja=MovimientoCaja.TipoCaja.YAPE).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        pagos_tarjeta = pagos_hoy.filter(tipo_caja=MovimientoCaja.TipoCaja.TARJETA).aggregate(total=Sum('monto')).get('total') or Decimal('0')

        return Response({
            'habitaciones': {
                'total': habitaciones.count(),
                'ocupadas': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.OCUPADO).count(),
                'disponibles': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE).count(),
                'limpieza': habitaciones.filter(estado_limpieza=Habitacion.EstadoLimpieza.SUCIO).count(),
                'mantenimiento': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.BLOQUEADO).count(),
            },
            'ingresos_hoy': {
                'hotel': ingresos_hotel,
                'market': ingresos_market,
                'cochera': ingresos_cochera,
                'total': total_ingresos,
            },
            'deudas_pendientes': {
                'cantidad': deudas_qs.count() + checkins_activos.filter(monto_deuda__gt=0).count(),
                'total': deudas_total + (checkins_activos.aggregate(total=Sum('monto_deuda')).get('total') or Decimal('0')),
            },
            'checkouts_proximos': [
                {
                    'id': checkin.id,
                    'habitacion': checkin.habitacion.numero,
                    'huesped': str(checkin.huesped),
                    'fecha_salida_estimada': checkin.fecha_salida_estimada,
                    'hora_salida_estimada': checkin.hora_salida_estimada,
                    'monto_deuda': checkin.monto_deuda,
                }
                for checkin in checkins_activos.order_by('fecha_salida_estimada', 'hora_salida_estimada')[:10]
            ],
            'reservas_hoy': [
                {
                    'id': reserva.id,
                    'huesped': str(reserva.huesped),
                    'habitacion_preferida': reserva.habitacion_preferida.numero,
                    'estado': reserva.estado,
                    'hora_llegada_estimada': reserva.hora_llegada_estimada,
                    'monto_adelanto': reserva.monto_adelanto,
                    'alerta_color': reserva.alerta_color,
                }
                for reserva in reservas_hoy[:10]
            ],
            'grafico_pagos': {
                'efectivo': pagos_efectivo,
                'yape': pagos_yape,
                'tarjeta': pagos_tarjeta,
            },
            'productos_stock_bajo': [
                {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'stock_actual': producto.stock_actual,
                    'stock_minimo': producto.stock_minimo,
                    'categoria': producto.categoria,
                }
                for producto in productos_stock_bajo[:10]
            ],
            'ultimos_movimientos': [
                {
                    'id': movimiento.id,
                    'tipo': movimiento.tipo,
                    'tipo_caja': movimiento.tipo_caja,
                    'modulo': movimiento.modulo,
                    'referencia': movimiento.referencia,
                    'monto': movimiento.monto,
                    'descripcion': movimiento.descripcion,
                    'fecha_hora': movimiento.fecha_hora,
                }
                for movimiento in movimientos_hoy[:10]
            ],
            'resumen': {
                'habitaciones': habitaciones.count(),
                'recados_no_leidos': Recado.objects.filter(leido=False).count(),
                'cajas_abiertas': Caja.objects.filter(estado=Caja.Estado.ABIERTA).count(),
                'espacios_libres': EspacioCochera.objects.filter(estado=EspacioCochera.Estado.LIBRE).count(),
            },
        })

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra el dashboard del sistema en una sola vista.
# O - Open/Closed: métricas nuevas se agregan extendiendo la respuesta sin reestructurar el API.
# L - Liskov Substitution: la vista cumple el contrato de APIView de DRF.
# I - Interface Segregation: expone únicamente el resumen que necesita el frontend.
# D - Dependency Inversion: depende de modelos como abstracciones de dominio y no de SQL crudo.
# ════════════════════════════════════════
