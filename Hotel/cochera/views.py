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


def _user_can_access_cochera(user):
    try:
        rol = getattr(user, 'rol', '') or ''
        return rol.lower() in ('admin', 'recepcionista') or user.is_superuser
    except Exception:
        return False


class EspacioCocheraViewSet(viewsets.ModelViewSet):
    queryset = EspacioCochera.objects.all().order_by('numero')
    serializer_class = EspacioCocheraSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not _user_can_access_cochera(self.request.user):
            return RegistroVehiculo.objects.none()
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        espacios = serializer.data

        # Enriquecemos cada espacio con información del vehículo actual si existe
        enriched = []
        for idx, espacio_obj in enumerate(queryset):
            espacio_data = espacios[idx]
            registro = RegistroVehiculo.objects.filter(espacio=espacio_obj, fecha_salida__isnull=True).order_by('-fecha_entrada', '-hora_entrada').first()
            if registro:
                espacio_data['vehiculo_actual'] = {
                    'id': registro.id,
                    'placa': registro.placa,
                    'tipo_cliente': registro.tipo_cliente,
                    'hora_ingreso': registro.hora_entrada.strftime('%H:%M') if registro.hora_entrada else None,
                    'fecha_ingreso': registro.fecha_entrada.strftime('%Y-%m-%d') if registro.fecha_entrada else None,
                }
                # Mantener compatibilidad con frontend anterior
                espacio_data['placa'] = registro.placa
                espacio_data['hora_ingreso'] = registro.hora_entrada.strftime('%H:%M') if registro.hora_entrada else None
            else:
                espacio_data['vehiculo_actual'] = None
                espacio_data['placa'] = None
                espacio_data['hora_ingreso'] = None
            enriched.append(espacio_data)

        return Response(enriched)


class EspacioCocheraDisponiblesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not _user_can_access_cochera(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = EspacioCochera.objects.filter(estado=EspacioCochera.Estado.LIBRE).order_by('numero')
        return Response(EspacioCocheraSerializer(queryset, many=True).data)


class RegistroVehiculoIngresoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not _user_can_access_cochera(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = RegistroVehiculoIngresoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registro = RegistroVehiculoService().registrar_ingreso(serializer.validated_data, request.user)
        return Response(_serializar_registro(registro), status=status.HTTP_201_CREATED)


class RegistroVehiculoSalidaView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, registro_id):
        if not _user_can_access_cochera(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        # Retorna el registro enriquecido con el monto calculado sin consumar la salida
        registro = RegistroVehiculo.objects.select_related('espacio', 'trabajador', 'checkin_vinculado').get(pk=registro_id)
        monto = RegistroVehiculoService().calcular_monto_para_registro(registro_id)
        data = _serializar_registro(registro)
        data['monto_calculado'] = monto
        return Response(data)

    def patch(self, request, registro_id):
        if not _user_can_access_cochera(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        registro_obj = RegistroVehiculo.objects.filter(pk=registro_id).first()

        if not registro_obj:
            return Response({"detail": "Registro no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Si el vehículo está vinculado a un check-in del hotel, se procesa por el flujo de Check-Out
        if registro_obj.checkin_vinculado_id is not None:
            return Response(
                {
                    "detail": "Este vehículo está vinculado a un hospedaje y se debe liquidar desde el módulo Hotel (Check-Out)."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Procesamos la salida para clientes públicos
        registro = RegistroVehiculoService().registrar_salida(registro_id)
        metodo = request.data.get('metodo_pago', MovimientoCaja.TipoCaja.EFECTIVO)

        caja_activa = Caja.objects.filter(
            trabajador=request.user,
            estado=Caja.Estado.ABIERTA
        ).order_by('-fecha_apertura', '-hora_apertura').first()

        monto_mov = getattr(registro, 'monto_total', None)
        try:
            from decimal import Decimal
            monto_mov = Decimal(str(monto_mov or 0))
        except Exception:
            monto_mov = None

        if caja_activa and (monto_mov is None or monto_mov == 0):
            tipo_caja = MovimientoCaja.TipoCaja.EFECTIVO
            metodo_up = str(metodo).upper() if metodo else None
            if metodo_up in (MovimientoCaja.TipoCaja.EFECTIVO, MovimientoCaja.TipoCaja.YAPE, MovimientoCaja.TipoCaja.TARJETA):
                tipo_caja = metodo_up

            monto_mov = RegistroVehiculoService().calcular_monto_para_registro(registro.id)

            MovimientoCaja.objects.create(
                caja=caja_activa,
                trabajador=caja_activa.trabajador,
                turno=caja_activa.turno,
                bloqueado=False,
                tipo=MovimientoCaja.Tipo.INGRESO,
                tipo_caja=tipo_caja,
                modulo=MovimientoCaja.Modulo.COCHERA,
                referencia=registro.placa,
                monto=monto_mov,
                descripcion=f'Salida de vehículo {registro.placa}',
                pagada=True,
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
