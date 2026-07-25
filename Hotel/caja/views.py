from collections import defaultdict
from datetime import date
from django.utils import timezone
from django.db.models import F, Sum, Q

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
from hotel.models import Habitacion
from market.models import DetalleVenta
from caja.serializers import (
    CajaAperturaSerializer,
    CajaCierreSerializer,
    CajaSerializer,
    MovimientoCajaInputSerializer,
    MovimientoCajaSerializer,
)
from caja.services import CajaService, MovimientoCajaService



def _caja_activa(user):
    hoy = timezone.localdate()
    turno_usuario = getattr(user, 'turno', None)

    filtros = {
        'trabajador': user,
        'estado': Caja.Estado.ABIERTA,
        'fecha_apertura': hoy,
    }
    if turno_usuario:
        filtros['turno'] = turno_usuario

    caja = Caja.objects.filter(**filtros).order_by('-fecha_apertura', '-hora_apertura').first()
    if caja:
        return caja

    # Fallback controlado: mismo usuario y misma fecha local, incluso si cambió de turno en su perfil.
    return Caja.objects.filter(
        trabajador=user,
        estado=Caja.Estado.ABIERTA,
        fecha_apertura=hoy,
    ).order_by('-fecha_apertura', '-hora_apertura').first()
    



def _serializar_resumen(caja):
    resumen = CajaService().obtener_resumen(caja)
    movimientos_qs = resumen['movimientos'].order_by('-fecha_hora')
    
    movimientos_serializados = MovimientoCajaSerializer(movimientos_qs, many=True).data
    
    agrupados = defaultdict(list)
    for movimiento in movimientos_qs:
        clave_modulo = movimiento.modulo.lower()
        agrupados[clave_modulo].append(MovimientoCajaSerializer(movimiento).data)
        
    return {
        'caja': CajaSerializer(caja).data,
        'monto_inicial': resumen['monto_inicial'],
        'total_efectivo': resumen['total_efectivo'],
        'total_yape': resumen['total_yape'],
        'total_tarjeta': resumen['total_tarjeta'],
        'total_ingresos': resumen['total_ingresos'],
        'total_egresos': resumen['total_egresos'],
        'total_general': resumen['total_general'],  # <-- AGREGADO: Envía el total real al JSON del Frontend
        'deudas_pendientes': MovimientoCajaSerializer(resumen['deudas_pendientes'], many=True).data,
        'movimientos': movimientos_serializados,
        'movimientos_por_modulo': {modulo: items for modulo, items in agrupados.items()},
    }


class CajaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Caja.objects.select_related('trabajador').order_by('-fecha_apertura', '-hora_apertura')
        return Response(CajaSerializer(queryset, many=True).data)


class CajaAperturaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CajaAperturaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            caja = CajaService().abrir_caja(serializer.validated_data, request.user)
            return Response(CajaSerializer(caja).data, status=status.HTTP_201_CREATED)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class CajaCierreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        caja = _caja_activa(request.user) 
        
        if not caja:
            return Response({'detail': 'No existe una caja abierta para este usuario.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CajaCierreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        caja_cerrada = CajaService().cerrar_caja(caja)
        return Response(CajaSerializer(caja_cerrada).data)


class CajaResumenView(APIView):
    permission_classes = [IsAuthenticated]

    def _parse_date(self, value):
        try:
            return date.fromisoformat(value)
        except Exception:
            return None

    def _build_date_range(self, request):
        periodo = request.query_params.get('periodo', '').strip().lower()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        hoy = timezone.localdate()

        if periodo:
            if periodo == 'hoy':
                return hoy, hoy
            if periodo == 'ayer':
                ayer = hoy - timezone.timedelta(days=1)
                return ayer, ayer
            if periodo == 'semana':
                inicio = hoy - timezone.timedelta(days=hoy.weekday())
                return inicio, hoy
            if periodo == 'quincena':
                inicio = hoy - timezone.timedelta(days=14)
                return inicio, hoy
            if periodo == 'mes':
                inicio = hoy.replace(day=1)
                return inicio, hoy

        if fecha_inicio:
            fecha_inicio_parsed = self._parse_date(fecha_inicio)
            if not fecha_inicio_parsed:
                return None, None
        else:
            fecha_inicio_parsed = None

        if fecha_fin:
            fecha_fin_parsed = self._parse_date(fecha_fin)
            if not fecha_fin_parsed:
                return None, None
        else:
            fecha_fin_parsed = fecha_inicio_parsed

        return fecha_inicio_parsed, fecha_fin_parsed

    def _get_movimientos_queryset(self, request):
        queryset = MovimientoCaja.objects.select_related('caja', 'trabajador')
        trabajador_id = request.query_params.get('trabajador_id')
        turno = request.query_params.get('turno')
        fecha_inicio, fecha_fin = self._build_date_range(request)

        if trabajador_id:
            queryset = queryset.filter(trabajador_id=trabajador_id)
        if turno:
            queryset = queryset.filter(turno=turno)
        if fecha_inicio and fecha_fin:
            start_dt = timezone.make_aware(timezone.datetime.combine(fecha_inicio, timezone.datetime.min.time()))
            end_dt = timezone.make_aware(timezone.datetime.combine(fecha_fin, timezone.datetime.max.time()))
            queryset = queryset.filter(fecha_hora__gte=start_dt, fecha_hora__lte=end_dt)

        return queryset.order_by('-fecha_hora')

    def get(self, request):
        try:
            if not request.query_params:
                caja_activa = _caja_activa(request.user)
                if caja_activa:
                    response = _serializar_resumen(caja_activa)
                    response['caja_activa'] = True
                    return Response(response)
                return Response({'caja_activa': False})

            fecha_inicio, fecha_fin = self._build_date_range(request)
            if request.query_params.get('fecha_inicio') and fecha_inicio is None:
                return Response({'detail': 'fecha_inicio inválida, use YYYY-MM-DD o periodo válido.'}, status=status.HTTP_400_BAD_REQUEST)
            if request.query_params.get('fecha_fin') and fecha_fin is None:
                return Response({'detail': 'fecha_fin inválida, use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

            movimientos = self._get_movimientos_queryset(request)
            filtro_aplicado = any(
                [request.query_params.get('fecha_inicio'), request.query_params.get('fecha_fin'), request.query_params.get('periodo'), request.query_params.get('trabajador_id'), request.query_params.get('turno')]
            )

            totales = {
                'total_ingresos': float(movimientos.filter(tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0),
                'total_egresos': float(movimientos.filter(tipo=MovimientoCaja.Tipo.EGRESO).aggregate(total=Sum('monto')).get('total') or 0),
                'total_general': float(
                    movimientos.filter(tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0
                ) - float(
                    movimientos.filter(tipo=MovimientoCaja.Tipo.EGRESO).aggregate(total=Sum('monto')).get('total') or 0
                ),
            }

            desglose_pago = {
                'efectivo': float(movimientos.filter(tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0),
                'yape': float(movimientos.filter(tipo_caja=MovimientoCaja.TipoCaja.YAPE, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0),
                'tarjeta': float(movimientos.filter(tipo_caja=MovimientoCaja.TipoCaja.TARJETA, tipo=MovimientoCaja.Tipo.INGRESO).aggregate(total=Sum('monto')).get('total') or 0),
            }

            response = {
                'filtros': {
                    'fecha_inicio': fecha_inicio.isoformat() if fecha_inicio else None,
                    'fecha_fin': fecha_fin.isoformat() if fecha_fin else None,
                    'trabajador_id': request.query_params.get('trabajador_id'),
                    'turno': request.query_params.get('turno'),
                    'periodo': request.query_params.get('periodo'),
                },
                'consolidado': totales,
                'desglose_pago': desglose_pago,
                'total_movimientos': movimientos.count(),
            }

            if filtro_aplicado:
                response['detalle'] = MovimientoCajaSerializer(movimientos, many=True).data

            return Response(response)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.localdate()

        # Calculamos rango de fecha/hora local para hoy y usamos intervalo [start, end)
        from datetime import datetime, time, timedelta
        start = timezone.make_aware(datetime.combine(hoy, time.min))
        end = start + timedelta(days=1)

        # Sumamos todos los movimientos reales de tipo INGRESO creados en el intervalo local de hoy
        total_ingresos = MovimientoCaja.objects.filter(
            fecha_hora__gte=start,
            fecha_hora__lt=end,
            tipo=MovimientoCaja.Tipo.INGRESO
        ).aggregate(total=Sum('monto'))['total'] or 0

        caja_activa_existe = Caja.objects.filter(fecha_apertura=hoy, estado__iexact='ABIERTA').exists()

        # Sumatoria de totales de todas las cajas abiertas (independiente del día)
        cajas_activas_qs = Caja.objects.filter(estado__iexact='ABIERTA')
        suma_cajas_activas = 0
        caja_service = CajaService()
        for caja in cajas_activas_qs:
            try:
                resumen_caja = caja_service.obtener_resumen(caja)
                suma_cajas_activas += float(resumen_caja.get('total_general', 0))
            except Exception:
                continue

        # 2. Estadísticas de Habitaciones
        total_habs = Habitacion.objects.count()
        ocupadas = Habitacion.objects.filter(estado_ocupacion='OCUPADO').count()
        disponibles = Habitacion.objects.filter(estado_ocupacion='DISPONIBLE').exclude(estado_limpieza='SUCIO').count()
        limpieza = Habitacion.objects.filter(estado_limpieza='SUCIO').count()
        # Contar habitaciones con estado RESERVADO (visibles para Recepción)
        reservadas = Habitacion.objects.filter(estado_ocupacion=Habitacion.EstadoOcupacion.RESERVADO).count()

        # 3. CORRECCIÓN ROBUSTA: Deudas pendientes SOLO de CheckIn activos sin salida
        # Lógica:
        # - Solo contar CheckIn con estado=ACTIVO
        # - Adicional: validar que fecha_salida_real sea NULL (no ha salido realmente)
        # - Sumar monto_deuda de estos CheckIn
        from hotel.models import CheckIn, Reserva

        suma_deudas_activas = CheckIn.objects.filter(
            Q(estado=CheckIn.Estado.ACTIVO) & Q(fecha_salida_real__isnull=True)
        ).aggregate(total=Sum('monto_deuda'))['total'] or 0

        # Contar reservas activas (pendientes o confirmadas para check-in).
        # Alineamos al día local: consideramos reservas cuya llegada es hoy o futura.
        reservas_qs = Reserva.objects.filter(
            estado__in=[Reserva.Estado.PENDIENTE, Reserva.Estado.CONFIRMADA_CHECKIN],
            fecha_llegada_estimada__gte=hoy
        )
        reservas_activas_count = reservas_qs.count()
        monto_custodia = reservas_qs.aggregate(total=Sum('monto_garantia')).get('total') or 0

        productos_vendidos_hoy = DetalleVenta.objects.filter(
            venta__fecha=hoy
        ).values(
            nombre=F('producto__nombre')
        ).annotate(
            cantidad=Sum('cantidad')
        ).order_by('-cantidad')[:5]

        return Response({
            "habitaciones": {
                "total": total_habs,
                "ocupadas": ocupadas,
                "disponibles": disponibles,
                "limpieza": limpieza,
                "reservadas": reservadas,
            },
            "ingresosDia": float(total_ingresos),
            "cajaActiva": caja_activa_existe,
            "sumaCajasActivas": float(suma_cajas_activas),
            "deudasPendientes": float(suma_deudas_activas),
            "proximosCheckouts": 0,
            "productosMasVendidos": [
                {"nombre": item["nombre"], "cantidad": item["cantidad"]}
                for item in productos_vendidos_hoy
            ]
            ,
            "reservas_activas": reservas_activas_count,
            "monto_custodia": float(monto_custodia),
        })

class MovimientoCajaViewSet(viewsets.ModelViewSet):
    queryset = MovimientoCaja.objects.select_related('caja').order_by('-fecha_hora')
    serializer_class = MovimientoCajaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        caja_id = self.request.query_params.get('caja_id')
        modulo = self.request.query_params.get('modulo')
        fecha = self.request.query_params.get('fecha')
        if caja_id:
            queryset = queryset.filter(caja_id=caja_id)
        if modulo:
            queryset = queryset.filter(modulo=modulo)
        if fecha:
            queryset = queryset.filter(fecha_hora__date=fecha)
        return queryset

    def create(self, request, *args, **kwargs):
        # CORRECCIÓN: Pasamos el request.user para evitar un quiebre de consistencia
        caja = _caja_activa(request.user)
        if not caja:
            return Response({'detail': 'No existe una caja abierta.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = MovimientoCajaInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movimiento = MovimientoCajaService().agregar_movimiento(serializer.validated_data, caja)
        return Response(MovimientoCajaSerializer(movimiento).data, status=status.HTTP_201_CREATED)


class MovimientoCajaPagarDeudaView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, movimiento_id):
        movimiento = MovimientoCaja.objects.get(pk=movimiento_id)
        if movimiento.tipo != MovimientoCaja.Tipo.DEUDA:
            return Response({'detail': 'El movimiento no es una deuda.'}, status=status.HTTP_400_BAD_REQUEST)
        movimiento = MovimientoCajaService().pagar_deuda(movimiento)
        return Response(MovimientoCajaSerializer(movimiento).data)


class HealthCajaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'module': 'caja', 'status': 'ok'})


# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: cada vista atiende una sola operación de caja.
# O - Open/Closed: nuevos reportes o filtros se añaden como clases separadas.
# L - Liskov Substitution: las vistas cumplen el contrato DRF esperado.
# I - Interface Segregation: apertura, cierre, resumen y movimientos quedan separados.
# D - Dependency Inversion: la capa web consume servicios y serializers en lugar de SQL directo.
# ════════════════════════════════════════
