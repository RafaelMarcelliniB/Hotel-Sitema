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
from users.models import Trabajador


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def _obtener_caja_activa(self, user):
        """
        Busca la caja abierta del usuario actual.
        
        Retorna: Objeto Caja con estado='ABIERTA' o None
        """
        return Caja.objects.filter(
            trabajador=user,
            estado=Caja.Estado.ABIERTA
        ).order_by('-fecha_apertura', '-hora_apertura').first()

    def _es_empleado(self, user):
        """Verifica si el usuario es Cajero o Recepcionista"""
        return user.rol in [Trabajador.Rol.CAJERO, Trabajador.Rol.RECEPCIONISTA]

    def _es_admin(self, user):
        """Verifica si el usuario es Administrador"""
        return user.rol == Trabajador.Rol.ADMIN

    def _obtener_movimientos_filtrados(self, request, hoy):
        """
        Retorna los movimientos de caja filtrados según el rol del usuario.
        
        - ADMIN: todos los movimientos del día
        - EMPLEADO CON CAJA ABIERTA: solo movimientos de su caja activa
        - EMPLEADO SIN CAJA: conjunto vacío (sin movimientos)
        """
        if self._es_admin(request.user):
            # Admin ve todos los movimientos del día
            return MovimientoCaja.objects.filter(fecha_hora__date=hoy).order_by('-fecha_hora')
        
        # Para empleados, buscamos su caja activa
        caja_activa = self._obtener_caja_activa(request.user)
        
        if caja_activa:
            # Si existe caja abierta, filtramos por esa caja específicamente
            return MovimientoCaja.objects.filter(caja=caja_activa).order_by('-fecha_hora')
        
        # Si no hay caja abierta, retornamos un queryset vacío
        return MovimientoCaja.objects.none()

    def get(self, request):
        hoy = timezone.localdate()
        habitaciones = Habitacion.objects.all()
        checkins_activos = CheckIn.objects.filter(estado=CheckIn.Estado.ACTIVO).select_related('habitacion', 'huesped')
        reservas_hoy = Reserva.objects.filter(fecha_llegada_estimada=hoy).select_related('huesped', 'habitacion_preferida')
        productos_stock_bajo = Producto.objects.filter(activo=True, stock_actual__lte=F('stock_minimo')).order_by('nombre')
        
        # Aplicar filtrado de movimientos según el rol del usuario
        movimientos_hoy = self._obtener_movimientos_filtrados(request, hoy)
        pagos_hoy = movimientos_hoy.filter(tipo=MovimientoCaja.Tipo.INGRESO)

        ingresos_hotel = movimientos_hoy.filter(modulo=MovimientoCaja.Modulo.HOTEL, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        ingresos_market = movimientos_hoy.filter(modulo=MovimientoCaja.Modulo.MARKET, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        ingresos_cochera = movimientos_hoy.filter(modulo=MovimientoCaja.Modulo.COCHERA, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        total_ingresos = ingresos_hotel + ingresos_market + ingresos_cochera

        # ════════════════════════════════════════════════════════════════════════════════════════
        # 🔧 DISEÑO REDISEÑADO - DASHBOARD SOLAMENTE CON INGRESOS REALES:
        # ════════════════════════════════════════════════════════════════════════════════════════
        # CAMBIO ARQUITECTÓNICO:
        # - Se elimina completamente la tarjeta "Deudas Pendientes" del Dashboard del Admin
        # - Los registros tipo='DEUDA' pertenecen ÚNICAMENTE al control de caja del recepcionista
        # - Las métricas financieras del Admin SOLO suman MovimientoCaja con tipo='INGRESO'
        # - Esto simplifica el Dashboard y elimina distorsiones en las métricas globales
        # ════════════════════════════════════════════════════════════════════════════════════════

        pagos_efectivo = pagos_hoy.filter(tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        pagos_yape = pagos_hoy.filter(tipo_caja=MovimientoCaja.TipoCaja.YAPE, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')
        pagos_tarjeta = pagos_hoy.filter(tipo_caja=MovimientoCaja.TipoCaja.TARJETA, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or Decimal('0')

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
                'recados_no_leidos': Recado.objects.exclude(estado=Recado.Estado.RESUELTO).count(),
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