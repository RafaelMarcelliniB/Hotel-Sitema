from django.db.models import Count, Sum
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja, MovimientoCaja
from cochera.models import EspacioCochera, RegistroVehiculo
from hotel.models import CheckIn, Habitacion, Huesped
from market.models import Producto, VentaMarket
from recados.models import Recado


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        habitaciones = Habitacion.objects.all()
        productos = Producto.objects.filter(activo=True)
        recados = Recado.objects.all().order_by('-fecha')[:5]
        checkins_activos = CheckIn.objects.filter(estado=CheckIn.Estado.ACTIVO)
        ventas = VentaMarket.objects.all()
        cajas = Caja.objects.all()
        espacios = EspacioCochera.objects.all()

        return Response({
            'habitaciones': {
                'total': habitaciones.count(),
                'ocupadas': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.OCUPADO).count(),
                'disponibles': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.DISPONIBLE).count(),
                'limpieza': habitaciones.filter(estado_limpieza=Habitacion.EstadoLimpieza.SUCIO).count(),
                'mantenimiento': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.BLOQUEADO).count(),
                'reservadas': habitaciones.filter(estado_ocupacion=Habitacion.EstadoOcupacion.RESERVADO).count(),
            },
            'ingresosDia': str(
                (ventas.aggregate(total=Sum('total'))['total'] or 0)
            ),
            'deudasPendientes': str(
                (checkins_activos.aggregate(total=Sum('monto_deuda'))['total'] or 0)
            ),
            'proximosCheckouts': checkins_activos.count(),
            'pagos': [
                {'name': 'Efectivo', 'value': ventas.filter(metodo_pago=VentaMarket.MetodoPago.EFECTIVO).count()},
                {'name': 'Yape', 'value': ventas.filter(metodo_pago=VentaMarket.MetodoPago.YAPE).count()},
                {'name': 'Tarjeta', 'value': ventas.filter(metodo_pago=VentaMarket.MetodoPago.TARJETA).count()},
            ],
            'ocupacionPorTipo': [
                {'name': tipo, 'ocupadas': habitaciones.filter(tipo=tipo, estado_ocupacion=Habitacion.EstadoOcupacion.OCUPADO).count()}
                for tipo, _ in Habitacion.Tipo.choices[:4]
            ],
            'ingresosSemana': [],
            'productosMasVendidos': [
                {'name': producto.nombre, 'ventas': producto.detalles_venta.aggregate(total=Sum('cantidad'))['total'] or 0}
                for producto in productos.order_by('nombre')[:4]
            ],
            'horasPico': [],
            'resumen': {
                'habitaciones': habitaciones.count(),
                'productos': productos.count(),
                'recados': recados.count(),
                'cajas_abiertas': cajas.filter(estado=Caja.Estado.ABIERTA).count(),
                'espacios_libres': espacios.filter(estado=EspacioCochera.Estado.LIBRE).count(),
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
