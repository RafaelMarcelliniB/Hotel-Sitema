from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import Q
from django.db import models
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from caja.models import Caja, MovimientoCaja
from users.models import Trabajador
from cochera.models import RegistroVehiculo
from cochera.services import RegistroVehiculoService
from hotel.models import CargoAdicional, CheckIn, CheckOut, Habitacion, Huesped, Reserva
from hotel.serializers import (
    CargoAdicionalCreateSerializer,
    CargoAdicionalSerializer,
    CheckInCreateSerializer,
    CheckOutCreateSerializer,
    CheckOutSerializer,
    HabitacionEstadoSerializer,
    HabitacionSerializer,
    HuespedSerializer,
    ReservaSerializer,
)
from hotel.repositories import CheckInRepository, HabitacionRepository
from hotel.services import CheckInService, CheckOutService
from market.models import VentaMarket


def _to_decimal(value):
    if value is None:
        return Decimal('0')
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal('0')


def _caja_activa(user):
    """Auxiliar para obtener la caja abierta del trabajador actual."""
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

    return Caja.objects.filter(
        trabajador=user,
        estado=Caja.Estado.ABIERTA,
        fecha_apertura=hoy,
    ).order_by('-fecha_apertura', '-hora_apertura').first()


def _tarifa_checkin(checkin):
    if checkin.turno_ingreso == CheckIn.TurnoIngreso.DIA:
        return checkin.habitacion.tarifa_dia
    if checkin.turno_ingreso == CheckIn.TurnoIngreso.NOCHE:
        return checkin.habitacion.tarifa_noche
    return checkin.habitacion.tarifa_madrugada


def _calcular_resumen_checkin(checkin):
    cochera_service = RegistroVehiculoService()
    subtotal_habitacion = _tarifa_checkin(checkin)
    subtotal_adicionales = checkin.cargos_adicionales.aggregate(total=Sum('monto')).get('total') or Decimal('0')
    ventas = VentaMarket.objects.filter(checkin_vinculado=checkin)
    subtotal_market = ventas.aggregate(total=Sum('total')).get('total') or Decimal('0')

    subtotal_cochera = Decimal('0')
    vehiculos = RegistroVehiculo.objects.filter(
        Q(checkin_vinculado=checkin) | Q(dni_conductor=checkin.huesped.dni_pasaporte)
    )

    for v in vehiculos:
        if v.fecha_salida is not None and v.monto_total is not None:
            subtotal_cochera += Decimal(str(v.monto_total))
        else:
            try:
                monto_actual = cochera_service._calcular_monto(v.tarifa_tipo, v.fecha_entrada, v.hora_entrada)
                subtotal_cochera += Decimal(str(monto_actual))
            except Exception:
                subtotal_cochera += Decimal(str(v.monto_total or 0))

    total_general = subtotal_habitacion + subtotal_adicionales + subtotal_market + subtotal_cochera
    return {
        'subtotal_habitacion': subtotal_habitacion,
        'subtotal_adicionales': subtotal_adicionales,
        'subtotal_market': subtotal_market,
        'subtotal_cochera': subtotal_cochera,
        'total_general': total_general,
    }


def _serializar_detalle_checkin(checkin):
    from django.db.models import Q

    if isinstance(checkin, tuple):
        checkin = checkin[0]

    checkin = CheckIn.objects.select_related('habitacion', 'huesped', 'trabajador').get(pk=checkin.pk)

    resumen = _calcular_resumen_checkin(checkin)
    cochera_service = RegistroVehiculoService()

    ventas = []
    for venta in checkin.ventas_market.prefetch_related('detalles', 'detalles__producto').all():
        ventas.append({
            'id': venta.id,
            'tipo_venta': venta.tipo_venta,
            'metodo_pago': venta.metodo_pago,
            'fecha': venta.fecha,
            'hora': venta.hora,
            'total': venta.total,
            'detalles': [
                {
                    'id': detalle.id,
                    'producto': detalle.producto.nombre,
                    'cantidad': detalle.cantidad,
                    'precio_unitario': detalle.precio_unitario,
                    'subtotal': detalle.subtotal,
                }
                for detalle in venta.detalles.all()
            ],
        })

    vehiculos = []
    vehiculos_query = RegistroVehiculo.objects.filter(
        Q(checkin_vinculado=checkin) | Q(dni_conductor=checkin.huesped.dni_pasaporte)
    )

    for v in vehiculos_query:
        monto_final = v.monto_total
        if v.fecha_salida is None:
            try:
                monto_final = cochera_service._calcular_monto(v.tarifa_tipo, v.fecha_entrada, v.hora_entrada)
            except Exception:
                monto_final = v.monto_total

        vehiculos.append({
            'id': v.id,
            'placa': v.placa,
            'tipo_vehiculo': v.tipo_vehiculo,
            'marca': v.marca,
            'color': v.color,
            'fecha_entrada': v.fecha_entrada,
            'hora_entrada': v.hora_entrada,
            'fecha_salida': v.fecha_salida,
            'hora_salida': v.hora_salida,
            'tarifa_tipo': v.tarifa_tipo,
            'monto_total': float(monto_final or 0),
            'tipo_cliente': getattr(v, 'tipo_cliente', None),
            'espacio_numero': getattr(v.espacio, 'numero', None),
        })

    cargos = CargoAdicionalSerializer(checkin.cargos_adicionales.all(), many=True).data
    entrada = timezone.make_aware(timezone.datetime.combine(checkin.fecha_entrada, checkin.hora_entrada))
    tiempo_transcurrido = timezone.localtime() - entrada

    monto_pago_adelantado = _to_decimal(checkin.monto_pagado)
    total_gral = resumen['total_general']
    saldo_pend = max(total_gral - monto_pago_adelantado, Decimal('0'))
    extras_combinados = float(resumen['subtotal_adicionales'] + resumen['subtotal_market'] + resumen['subtotal_cochera'])

    return {
        'id': checkin.id,
        'estado': checkin.estado,
        'turno_ingreso': checkin.turno_ingreso,
        'tipo_pago': checkin.tipo_pago,
        'monto_pagado': float(checkin.monto_pagado or 0.0),
        'monto_deuda': float(checkin.monto_deuda or 0.0),
        'es_pareja': checkin.es_pareja,
        'fecha_entrada': checkin.fecha_entrada,
        'hora_entrada': checkin.hora_entrada,
        'fecha_salida_estimada': checkin.fecha_salida_estimada,
        'hora_salida_estimada': checkin.hora_salida_estimada,
        'habitacion': HabitacionSerializer(checkin.habitacion).data,
        'huesped': HuespedSerializer(checkin.huesped).data,
        'cargos_adicionales': cargos,
        'ventas_market': ventas,
        'vehiculos_cochera': vehiculos,
        'vehiculos': vehiculos,
        'tiempo_transcurrido': str(tiempo_transcurrido),
        'monto_habitacion': float(resumen['subtotal_habitacion']),
        'monto_adicionales': extras_combinados,
        'total_pagar': float(total_gral),
        'saldo_pendiente': float(saldo_pend),
    }


class HabitacionViewSet(viewsets.ModelViewSet):
    queryset = Habitacion.objects.all().order_by('numero')
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        disponibles = self.request.query_params.get('disponibles')
        if disponibles and disponibles.lower() == 'true':
            return queryset.filter(
                estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE,
                estado_limpieza=Habitacion.EstadoLimpieza.LIMPIO,
            )
        return queryset

    @action(detail=False, methods=['get'], url_path='disponibles')
    def disponibles(self, request):
        queryset = self.get_queryset().filter(
            estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE,
            estado_limpieza=Habitacion.EstadoLimpieza.LIMPIO,
        )
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=['patch'], url_path='estado')
    def estado(self, request, pk=None):
        habitacion = self.get_object()
        serializer = HabitacionEstadoSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for field, value in serializer.validated_data.items():
            setattr(habitacion, field, value)
        habitacion.save()
        return Response(self.get_serializer(habitacion).data)

    @action(detail=True, methods=['post'], url_path='limpiar')
    def limpiar(self, request, pk=None):
        habitacion = self.get_object()
        habitacion.estado_limpieza = Habitacion.EstadoLimpieza.LIMPIO
        habitacion.save(update_fields=['estado_limpieza'])
        return Response(self.get_serializer(habitacion).data)

    @action(detail=True, methods=['post'], url_path='bloquear')
    def bloquear(self, request, pk=None):
        habitacion = self.get_object()
        habitacion.estado_ocupacion = Habitacion.EstadoOcupacion.BLOQUEADO
        habitacion.save(update_fields=['estado_ocupacion'])
        return Response(self.get_serializer(habitacion).data)

    # Permisos basados en rol: solo administradores pueden crear/editar/eliminar habitaciones
    def _es_admin(self, user):
        try:
            return getattr(user, 'rol', '').lower() == 'admin' or user.is_superuser
        except Exception:
            return False

    def create(self, request, *args, **kwargs):
        if not self._es_admin(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if not self._es_admin(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not self._es_admin(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not self._es_admin(request.user):
            return Response({'detail': 'Permisos insuficientes.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class HuespedViewSet(viewsets.ModelViewSet):
    queryset = Huesped.objects.all().order_by('apellido', 'nombre')
    serializer_class = HuespedSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        dni = self.request.query_params.get('dni') or self.request.query_params.get('dni_pasaporte')
        nombre = self.request.query_params.get('nombre')
        if dni:
            queryset = queryset.filter(dni_pasaporte=dni)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        return queryset


class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related('huesped', 'habitacion_preferida', 'trabajador').order_by('-fecha_llegada_estimada', '-hora_llegada_estimada')
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha = self.request.query_params.get('fecha')
        if fecha == 'hoy':
            fecha = timezone.localdate()
        if fecha:
            queryset = queryset.filter(fecha_llegada_estimada=fecha)
        return queryset

    @action(detail=True, methods=['patch'], url_path='confirmar')
    def confirmar(self, request, pk=None):
        reserva = self.get_object()
        reserva.estado = Reserva.Estado.CONFIRMADA
        reserva.save(update_fields=['estado'])
        return Response(self.get_serializer(reserva).data)


class CheckInCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 🔒 BLOQUEO DE SEGURIDAD: Validar que empleado tenga caja abierta
        if hasattr(request.user, 'rol') and request.user.rol != Trabajador.Rol.ADMIN:
            caja_existe = _caja_activa(request.user) is not None
            if not caja_existe:
                raise ValidationError(
                    "Debe aperturar su caja de turno antes de realizar esta operación."
                )
        
        serializer = CheckInCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        caja_activa = _caja_activa(request.user)

        if not caja_activa:
            return Response(
                {'error': 'No se puede realizar el check-in porque no existe una caja abierta para tu usuario/turno actual.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        checkin = CheckInService().iniciar_alquiler(serializer.validated_data, request.user)

        tarifa = _tarifa_checkin(checkin)
        descuento = _to_decimal(serializer.validated_data.get('descuento', 0))
        total_habitacion = tarifa - descuento
        monto_pagado = _to_decimal(serializer.validated_data.get('monto_pagado', 0))

        saldo_restante = total_habitacion - monto_pagado
        if saldo_restante > 0:
            MovimientoCaja.objects.create(
                caja=caja_activa,
                trabajador=caja_activa.trabajador,
                turno=caja_activa.turno,
                bloqueado=False,
                tipo=MovimientoCaja.Tipo.DEUDA,
                tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
                modulo=MovimientoCaja.Modulo.HOTEL,
                referencia=f'Check-in #{checkin.id}',
                monto=saldo_restante,
                descripcion=f'Costo de estadía pendiente hab. {checkin.habitacion.numero} - Huésped: {checkin.huesped.nombre}',
                pagada=False
            )

        return Response(_serializar_detalle_checkin(checkin), status=status.HTTP_201_CREATED)


class CheckOutCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, checkin_id):
        from django.db.models import Q
        checkin_repo = CheckInRepository()
        checkin = checkin_repo.get_by_id(checkin_id)

        if checkin.estado == CheckIn.Estado.CERRADO:
            return Response({"detail": "Este hospedaje ya cuenta con Check-Out."}, status=status.HTTP_400_BAD_REQUEST)

        # Intentamos cerrar automáticamente cochera vinculada
        vehiculo_activo = RegistroVehiculo.objects.filter(
            Q(checkin_vinculado_id=checkin_id) | Q(dni_conductor=checkin.huesped.dni_pasaporte),
            fecha_salida__isnull=True
        ).first()

        if vehiculo_activo:
            try:
                RegistroVehiculoService().registrar_salida(vehiculo_activo.id)
            except Exception as e:
                print(f"Aviso en automatización de cochera: {e}")

        checkin_actualizado = checkin_repo.get_by_id(checkin_id)

        cargos = checkin_actualizado.cargos_adicionales.all()
        subtotal_habitacion = CheckInService()._tarifa_habitacion(checkin_actualizado.habitacion, checkin_actualizado.turno_ingreso)
        subtotal_adicionales = sum((cargo.monto for cargo in cargos), Decimal('0.00'))

        try:
            subtotal_market = sum((venta.total for venta in checkin_actualizado.ventas_market.all()), Decimal('0.00'))
        except Exception:
            subtotal_market = Decimal('0.00')

        subtotal_cochera = sum(
            (v.monto_total for v in RegistroVehiculo.objects.filter(
                Q(checkin_vinculado_id=checkin_id) | Q(dni_conductor=checkin.huesped.dni_pasaporte)
            ) if v.monto_total is not None),
            Decimal('0.00')
        )

        total_general_decimal = subtotal_habitacion + subtotal_adicionales + subtotal_market + subtotal_cochera

        monto_adelantado = _to_decimal(checkin_actualizado.monto_pagado)
        saldo_pendiente_real = max(total_general_decimal - monto_adelantado, Decimal('0.00'))

        caja_activa = _caja_activa(request.user)
        if caja_activa and saldo_pendiente_real > 0:
            monto_movimiento = float(saldo_pendiente_real)
            metodo_pago_raw = request.data.get('metodo_pago', 'EFECTIVO').upper()
            tipo_caja = metodo_pago_raw if metodo_pago_raw in ['EFECTIVO', 'YAPE', 'TARJETA'] else 'EFECTIVO'

            MovimientoCaja.objects.create(
                caja=caja_activa,
                trabajador=caja_activa.trabajador,
                turno=caja_activa.turno,
                bloqueado=False,
                tipo=MovimientoCaja.Tipo.INGRESO,
                tipo_caja=tipo_caja,
                monto=monto_movimiento,
                modulo=MovimientoCaja.Modulo.HOTEL,
                descripcion=f"Check-Out Saldo Pendiente Habitación {checkin_actualizado.habitacion.numero} - Huésped: {checkin_actualizado.huesped.nombre} {checkin_actualizado.huesped.apellido}",
            )

        datos_checkout = {
            'subtotal_habitacion': float(subtotal_habitacion),
            'subtotal_adicionales': float(subtotal_adicionales),
            'subtotal_market': float(subtotal_market),
            'subtotal_cochera': float(subtotal_cochera),
            'total_general': float(total_general_decimal),
            'metodo_pago': request.data.get('metodo_pago', 'EFECTIVO').upper(),
        }

        checkout_obj = CheckOutService().finalizar_alquiler(checkin_id, datos_checkout, request.user)

        # Marcamos como pagadas las deudas relacionadas al check-in aunque no haya saldo pendiente
        MovimientoCaja.objects.filter(
            referencia=f'Check-in #{checkin.id}',
            tipo=MovimientoCaja.Tipo.DEUDA
        ).update(pagada=True)

        # Liberar automáticamente los espacios de cochera vinculados a este check-in
        vehiculos_por_salida = RegistroVehiculo.objects.filter(checkin_vinculado=checkin, fecha_salida__isnull=True)
        registro_service = RegistroVehiculoService()
        for reg in vehiculos_por_salida:
            try:
                registro_service.registrar_salida(reg.id)
            except Exception:
                continue

        return Response({
            "message": "Check-Out procesado con éxito.",
            "total_cochera": float(subtotal_cochera),
            "saldo_pagado": float(saldo_pendiente_real)
        }, status=status.HTTP_201_CREATED)


class CheckInActiveListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = (
            CheckIn.objects.filter(estado=CheckIn.Estado.ACTIVO)
            .select_related('habitacion', 'huesped', 'trabajador')
            .order_by('-fecha_entrada', '-hora_entrada')
        )
        return Response([_serializar_detalle_checkin(checkin) for checkin in queryset])


class CheckInDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, checkin_id):
        checkin = CheckIn.objects.select_related('habitacion', 'huesped', 'trabajador').get(pk=checkin_id)
        return Response(_serializar_detalle_checkin(checkin))


class CheckInCargoAdicionalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, checkin_id):
        checkin = CheckIn.objects.get(pk=checkin_id)
        serializer = CargoAdicionalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cargo = CheckInService().agregar_cargo_adicional(checkin, serializer.validated_data, request.user)
        return Response(CargoAdicionalSerializer(cargo).data, status=status.HTTP_201_CREATED)


class HealthHotelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'module': 'hotel', 'status': 'ok'})


# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO: documentación ligera sobre responsabilidades y diseño.
# ════════════════════════════════════════
