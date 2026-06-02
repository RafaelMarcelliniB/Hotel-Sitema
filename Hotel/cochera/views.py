from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
from cochera.models import EspacioCochera, RegistroVehiculo
from cochera.serializers import (
    EspacioCocheraInputSerializer,
    EspacioCocheraSerializer,
    RegistroVehiculoIngresoSerializer,
    RegistroVehiculoSerializer,
)
from cochera.services import EspacioCocheraService, RegistroVehiculoService


def _serializar_registro(registro):
    registro = RegistroVehiculo.objects.select_related('espacio', 'trabajador', 'checkin_vinculado').get(pk=registro.pk)
    return RegistroVehiculoSerializer(registro).data


class EspacioCocheraViewSet(viewsets.ModelViewSet):
    queryset = EspacioCochera.objects.all().order_by('numero')
    serializer_class = EspacioCocheraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset


class EspacioCocheraDisponiblesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = EspacioCochera.objects.filter(estado=EspacioCochera.Estado.LIBRE).order_by('numero')
        return Response(EspacioCocheraSerializer(queryset, many=True).data)


class RegistroVehiculoIngresoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RegistroVehiculoIngresoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registro = RegistroVehiculoService().registrar_ingreso(serializer.validated_data, request.user)
        return Response(_serializar_registro(registro), status=status.HTTP_201_CREATED)


class RegistroVehiculoSalidaView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, registro_id):
        registro = RegistroVehiculoService().registrar_salida(registro_id)
        caja_activa = Caja.objects.filter(estado=Caja.Estado.ABIERTA).order_by('-fecha_apertura', '-hora_apertura').first()
        if caja_activa:
            MovimientoCaja.objects.create(
                caja=caja_activa,
                tipo=MovimientoCaja.Tipo.INGRESO,
                tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
                modulo=MovimientoCaja.Modulo.COCHERA,
                referencia=registro.placa,
                monto=registro.monto_total,
                descripcion=f'Salida de vehículo {registro.placa}',
            )
        return Response(_serializar_registro(registro))


class RegistroVehiculoHistorialView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fecha = request.query_params.get('fecha')
        placa = request.query_params.get('placa')
        queryset = RegistroVehiculo.objects.select_related('espacio', 'trabajador', 'checkin_vinculado').order_by('-fecha_entrada', '-hora_entrada')
        if fecha:
            queryset = queryset.filter(fecha_entrada=fecha)
        if placa:
            queryset = queryset.filter(placa__icontains=placa)
        return Response(RegistroVehiculoSerializer(queryset, many=True).data)


class HealthCocheraView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'module': 'cochera', 'status': 'ok'})


# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: cada vista atiende un flujo concreto de cochera.
# O - Open/Closed: nuevos reportes o filtros se agregan como vistas o acciones aisladas.
# L - Liskov Substitution: el viewset y las vistas cumplen el contrato DRF.
# I - Interface Segregation: espacio, ingreso, salida e historial están separados.
# D - Dependency Inversion: la capa web consume servicios y serializers, no el ORM como regla de negocio.
# ════════════════════════════════════════
