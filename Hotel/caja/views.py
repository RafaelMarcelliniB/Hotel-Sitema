from collections import defaultdict
from datetime import date
from django.utils import timezone
from django.db.models import Sum

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
from hotel.models import Habitacion
from caja.serializers import (
    CajaAperturaSerializer,
    CajaCierreSerializer,
    CajaSerializer,
    MovimientoCajaInputSerializer,
    MovimientoCajaSerializer,
)
from caja.services import CajaService, MovimientoCajaService



def _caja_activa(user):
    # Intentamos ser lo más flexibles posible
    return Caja.objects.filter(
        trabajador=user, 
        estado__iexact='ABIERTA' # 'iexact' ignora si es mayúscula o minúscula
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
        caja = CajaService().abrir_caja(serializer.validated_data, request.user)
        return Response(CajaSerializer(caja).data, status=status.HTTP_201_CREATED)


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

    def get(self, request):
        try:
            caja = _caja_activa(request.user)
            
            if not caja:
                return Response(
                    {
                        'caja_activa': False,
                        'detail': 'Sin caja activa'
                    }, 
                    status=status.HTTP_200_OK
                )
            
            datos = _serializar_resumen(caja)
            datos['caja_activa'] = True
            return Response(datos)
            
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

        # 3. Sumatoria global de deudas pendientes basada en movimientos tipo DEUDA no pagados
        suma_deudas_mov = MovimientoCaja.objects.filter(tipo=MovimientoCaja.Tipo.DEUDA, pagada=False).aggregate(total=Sum('monto'))['total'] or 0

        return Response({
            "habitaciones": {
                "total": total_habs,
                "ocupadas": ocupadas,
                "disponibles": disponibles,
                "limpieza": limpieza
            },
            "ingresosDia": float(total_ingresos),
            "cajaActiva": caja_activa_existe,
            "sumaCajasActivas": float(suma_cajas_activas),
            "deudasPendientes": float(suma_deudas_mov),
            "proximosCheckouts": 0,
            "productosMasVendidos": []
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
