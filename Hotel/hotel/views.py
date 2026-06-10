from collections import defaultdict
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action  # <-- Reparado aquí
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
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


def _tarifa_checkin(checkin):
    if checkin.turno_ingreso == CheckIn.TurnoIngreso.DIA:
        return checkin.habitacion.tarifa_dia
    if checkin.turno_ingreso == CheckIn.TurnoIngreso.NOCHE:
        return checkin.habitacion.tarifa_noche
    return checkin.habitacion.tarifa_madrugada


def _calcular_resumen_checkin(checkin):
    subtotal_habitacion = _tarifa_checkin(checkin)
    subtotal_adicionales = checkin.cargos_adicionales.aggregate(total=Sum('monto')).get('total') or Decimal('0')
    ventas = VentaMarket.objects.filter(checkin_vinculado=checkin)
    subtotal_market = ventas.aggregate(total=Sum('total')).get('total') or Decimal('0')
    # Excluimos de la factura del huésped los registros de cochera que sean de tipo HUESPED
    vehiculos = RegistroVehiculo.objects.filter(checkin_vinculado=checkin)
    vehiculos_facturables = vehiculos.exclude(tipo_cliente=RegistroVehiculo.TipoCliente.HUESPED)
    subtotal_cochera = vehiculos_facturables.aggregate(total=Sum('monto_total')).get('total') or Decimal('0')
    total_general = subtotal_habitacion + subtotal_adicionales + subtotal_market + subtotal_cochera
    return {
        'subtotal_habitacion': subtotal_habitacion,
        'subtotal_adicionales': subtotal_adicionales,
        'subtotal_market': subtotal_market,
        'subtotal_cochera': subtotal_cochera,
        'total_general': total_general,
    }


def _serializar_detalle_checkin(checkin):
    checkin = CheckIn.objects.select_related('habitacion', 'huesped', 'trabajador').get(pk=checkin.pk)
    resumen = _calcular_resumen_checkin(checkin)
    
    ventas = []
    for venta in checkin.ventas_market.prefetch_related('detalles', 'detalles__producto').all():
        ventas.append(
            {
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
            }
        )
        
    vehiculos = [
        {
            'id': vehiculo.id,
            'placa': vehiculo.placa,
            'tipo_vehiculo': vehiculo.tipo_vehiculo,
            'marca': vehiculo.marca,
            'color': vehiculo.color,
            'fecha_entrada': vehiculo.fecha_entrada,
            'hora_entrada': vehiculo.hora_entrada,
            'fecha_salida': vehiculo.fecha_salida,
            'hora_salida': vehiculo.hora_salida,
            'tarifa_tipo': vehiculo.tarifa_tipo,
            'monto_total': vehiculo.monto_total,
            'tipo_cliente': vehiculo.tipo_cliente,
            'espacio_numero': getattr(vehiculo.espacio, 'numero', None),
        }
        for vehiculo in checkin.vehiculos.all()
    ]
    
    cargos = CargoAdicionalSerializer(checkin.cargos_adicionales.all(), many=True).data
    entrada = timezone.make_aware(timezone.datetime.combine(checkin.fecha_entrada, checkin.hora_entrada))
    tiempo_transcurrido = timezone.localtime() - entrada

    monto_pago_adelantado = _to_decimal(checkin.monto_pagado)
    total_gral = resumen['total_general']
    saldo_pend = max(total_gral - monto_pago_adelantado, Decimal('0'))

    return {
        'id': checkin.id,
        'estado': checkin.estado,
        'turno_ingreso': checkin.turno_ingreso,
        'tipo_pago': checkin.tipo_pago,
        'monto_pagado': checkin.monto_pagado,
        'monto_deuda': checkin.monto_deuda,
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
        'tiempo_transcurrido': str(tiempo_transcurrido),
        
        # MAPEO CLAVE PARA EL FRONTEND (ModalCheckOut.jsx)
        'monto_habitacion': resumen['subtotal_habitacion'],
        'monto_adicionales': resumen['subtotal_adicionales'] + resumen['subtotal_market'] + resumen['subtotal_cochera'],
        'total_pagar': total_gral,
        'saldo_pendiente': saldo_pend,
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
        serializer = CheckInCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Buscamos primero una caja abierta asignada al trabajador que realiza la acción.
        caja_activa = Caja.objects.filter(
            trabajador=request.user,
            estado__iexact='ABIERTA'
        ).order_by('-fecha_apertura', '-hora_apertura').first()

        # Si el trabajador no tiene caja, intentamos usar cualquier caja abierta en el sistema
        # (ej. cuando un admin o supervisor realiza el registro en nombre de otro).
        if not caja_activa:
            caja_activa = Caja.objects.filter(
                estado__iexact='ABIERTA'
            ).order_by('-fecha_apertura', '-hora_apertura').first()

        if not caja_activa:
            return Response(
                {'error': 'No se puede realizar el check-in porque no existe ninguna caja abierta en el sistema.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        checkin = CheckInService().iniciar_alquiler(serializer.validated_data, request.user)

        tarifa = _tarifa_checkin(checkin)
        descuento = _to_decimal(serializer.validated_data.get('descuento', 0))
        total_habitacion = tarifa - descuento

        # Solo creamos un movimiento de DEUDA si el huésped NO pagó el total al hacer el check-in
        monto_pagado = _to_decimal(checkin.monto_pagado)
        saldo_deuda = max(total_habitacion - monto_pagado, Decimal('0'))

        if saldo_deuda > 0:
            MovimientoCaja.objects.create(
                caja=caja_activa,
                tipo=MovimientoCaja.Tipo.DEUDA,
                tipo_caja=MovimientoCaja.TipoCaja.EFECTIVO,
                modulo=MovimientoCaja.Modulo.HOTEL,
                referencia=f'Check-in #{checkin.id}',
                monto=saldo_deuda,
                descripcion=f'Costo de estadía pendiente hab. {checkin.habitacion.numero} - Huésped: {checkin.huesped.nombre}',
                pagada=False
            )

        return Response(_serializar_detalle_checkin(checkin), status=status.HTTP_201_CREATED)


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


class CheckOutCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, checkin_id):
        checkin = CheckIn.objects.select_related('habitacion', 'huesped', 'trabajador').get(pk=checkin_id)
        serializer = CheckOutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        caja_activa = Caja.objects.filter(
            estado__iexact='ABIERTA'
        ).order_by('-fecha_apertura', '-hora_apertura').first()
        
        if not caja_activa:
            return Response(
                {'error': 'No se puede procesar la salida porque no existe ninguna caja abierta en el sistema.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        resumen = _calcular_resumen_checkin(checkin)
        monto_pago_adelantado = _to_decimal(checkin.monto_pagado)
        total_gral = resumen['total_general']
        saldo_pendiente = max(total_gral - monto_pago_adelantado, Decimal('0'))

        checkout_data = {
            'subtotal_habitacion': resumen['subtotal_habitacion'],
            'subtotal_adicionales': resumen['subtotal_adicionales'],
            'subtotal_market': resumen['subtotal_market'],
            'subtotal_cochera': resumen['subtotal_cochera'],
            'total_general': total_gral,
            'metodo_pago': serializer.validated_data['metodo_pago'],
            'deuda_pendiente': saldo_pendiente,
        }
        
        checkout = CheckOutService().finalizar_alquiler(checkin_id, checkout_data, request.user)
        
        if saldo_pendiente > 0:
            # Normalizamos el tipo de caja recibido desde el payload
            tipo_caja = serializer.validated_data.get('metodo_pago') or serializer.validated_data.get('tipo_pago') or 'EFECTIVO'
            if tipo_caja not in (MovimientoCaja.TipoCaja.EFECTIVO, MovimientoCaja.TipoCaja.YAPE, MovimientoCaja.TipoCaja.TARJETA):
                # Aceptamos valores en mayúsculas/minúsculas y mapeamos si es necesario
                tipo_caja = tipo_caja.upper()
            MovimientoCaja.objects.create(
                caja=caja_activa,
                tipo=MovimientoCaja.Tipo.INGRESO,
                tipo_caja=tipo_caja,
                modulo=MovimientoCaja.Modulo.HOTEL,
                referencia=f'Checkout #{checkin.id}',
                monto=saldo_pendiente,
                descripcion=f'Liquidación Check-out hab. {checkin.habitacion.numero} - Huésped: {checkin.huesped.nombre}',
                pagada=True
            )
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
                # No detener el flujo de checkout por errores en liberación de cochera;
                # si hay un problema se podrá revisar manualmente en registros.
                continue
        
        return Response(CheckOutSerializer(checkout).data, status=status.HTTP_201_CREATED)


class HealthHotelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'module': 'hotel', 'status': 'ok'})
    
    
# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: cada vista atiende un solo flujo del módulo hotel.
# O - Open/Closed: nuevos endpoints se agregan como clases aisladas sin tocar los existentes.
# L - Liskov Substitution: las vistas cumplen el contrato de DRF y pueden sustituirse por otras vistas equivalentes.
# I - Interface Segregation: check-in, check-out, habitaciones, huéspedes y reservas están separados por responsabilidad.
# D - Dependency Inversion: la capa web consume servicios y serializers, no consulta el ORM directamente para la lógica crítica.
# ════════════════════════════════════════