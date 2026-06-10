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
    def get(self, request, registro_id):
        # Retorna el registro enriquecido con el monto calculado sin consumar la salida
        registro = RegistroVehiculo.objects.select_related('espacio', 'trabajador', 'checkin_vinculado').get(pk=registro_id)
        monto = RegistroVehiculoService().calcular_monto_para_registro(registro_id)
        data = _serializar_registro(registro)
        data['monto_calculado'] = monto
        return Response(data)

    def patch(self, request, registro_id):
        # Primero intentamos obtener el registro actual sin ejecutar la salida aún
        registro = RegistroVehiculo.objects.select_related('espacio', 'trabajador', 'checkin_vinculado').get(pk=registro_id)
        caja_activa = Caja.objects.filter(estado=Caja.Estado.ABIERTA).order_by('-fecha_apertura', '-hora_apertura').first()

        # Si el registro ya tiene fecha_salida, no intentamos re-registrar la salida.
        if registro.fecha_salida:
            # Nos aseguramos de que exista un movimiento en caja para este registro; si no, lo creamos.
            if caja_activa:
                movimiento_existe = MovimientoCaja.objects.filter(
                    referencia=registro.placa,
                    modulo=MovimientoCaja.Modulo.COCHERA,
                    monto=registro.monto_total
                ).exists()
                if not movimiento_existe:
                    metodo = request.data.get('metodo_pago', None)
                    tipo_caja = MovimientoCaja.TipoCaja.EFECTIVO
                    if metodo:
                        metodo_up = str(metodo).upper()
                        if metodo_up in (MovimientoCaja.TipoCaja.EFECTIVO, MovimientoCaja.TipoCaja.YAPE, MovimientoCaja.TipoCaja.TARJETA):
                            tipo_caja = metodo_up
                    monto_mov = registro.monto_total or RegistroVehiculoService().calcular_monto_para_registro(registro.id)
                    MovimientoCaja.objects.create(
                        caja=caja_activa,
                        tipo=MovimientoCaja.Tipo.INGRESO,
                        tipo_caja=tipo_caja,
                        modulo=MovimientoCaja.Modulo.COCHERA,
                        referencia=registro.placa,
                        monto=monto_mov,
                        descripcion=f'Salida de vehículo {registro.placa}',
                        pagada=True,
                    )
            return Response(_serializar_registro(registro))

        # Si no tiene salida, procedemos a registrar la salida normalmente
        try:
            registro = RegistroVehiculoService().registrar_salida(registro_id)
        except ValueError as e:
            # Si por alguna razón el servicio detecta que ya salió, devolvemos el estado actual
            return Response({'detail': str(e)}, status=400)

        if caja_activa:
            # Accept payment method from request data
            metodo = request.data.get('metodo_pago', None)
            tipo_caja = MovimientoCaja.TipoCaja.EFECTIVO
            if metodo:
                metodo_up = str(metodo).upper()
                if metodo_up in (MovimientoCaja.TipoCaja.EFECTIVO, MovimientoCaja.TipoCaja.YAPE, MovimientoCaja.TipoCaja.TARJETA):
                    tipo_caja = metodo_up

            # Aseguramos que usamos el monto actualizado; si está vacío, recalculamos
            monto_mov = getattr(registro, 'monto_total', None)
            try:
                from decimal import Decimal
                if not monto_mov or Decimal(monto_mov) == Decimal('0'):
                    monto_mov = RegistroVehiculoService().calcular_monto_para_registro(registro.id)
            except Exception:
                monto_mov = RegistroVehiculoService().calcular_monto_para_registro(registro.id)

            MovimientoCaja.objects.create(
                caja=caja_activa,
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
