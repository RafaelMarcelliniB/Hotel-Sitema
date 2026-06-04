from collections import defaultdict

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
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
    movimientos = resumen['movimientos'].order_by('fecha_hora')
    agrupados = defaultdict(list)
    for movimiento in movimientos:
        agrupados[movimiento.modulo].append(MovimientoCajaSerializer(movimiento).data)
    return {
        'caja': CajaSerializer(caja).data,
        'monto_inicial': resumen['monto_inicial'],
        'total_efectivo': resumen['total_efectivo'],
        'total_yape': resumen['total_yape'],
        'total_tarjeta': resumen['total_tarjeta'],
        'total_ingresos': resumen['total_ingresos'],
        'total_egresos': resumen['total_egresos'],
        'deudas_pendientes': MovimientoCajaSerializer(resumen['deudas_pendientes'], many=True).data,
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
                # El 404 es correcto para que React sepa que no hay caja
                return Response(
                    {'detail': 'Sin caja activa'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Si hay caja, intentamos serializar
            datos = _serializar_resumen(caja)
            return Response(datos)
            
        except Exception as e:
            # Si algo falla en la lógica, que nos diga qué es
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        caja = _caja_activa()
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
