from django.db.models import F
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import IngresoMercaderia, Producto, VentaMarket
from market.serializers import (
	IngresoMercaderiaCreateSerializer,
	IngresoMercaderiaSerializer,
	ProductoSerializer,
	VentaMarketCreateSerializer,
	VentaMarketSerializer,
)
from market.services import IngresoMercaderiaService, VentaMarketService


def _serializar_venta(venta):
	venta = VentaMarket.objects.select_related('trabajador', 'checkin_vinculado').get(pk=venta.pk)
	return {
		'id': venta.id,
		'tipo_venta': venta.tipo_venta,
		'checkin_vinculado': venta.checkin_vinculado_id,
		'trabajador': venta.trabajador_id,
		'fecha': venta.fecha,
		'hora': venta.hora,
		'total': venta.total,
		'metodo_pago': venta.metodo_pago,
		'detalles': [
			{
				'id': detalle.id,
				'producto_id': detalle.producto_id,
				'producto': detalle.producto.nombre,
				'cantidad': detalle.cantidad,
				'precio_unitario': detalle.precio_unitario,
				'subtotal': detalle.subtotal,
			}
			for detalle in venta.detalles.select_related('producto').all()
		],
	}


class ProductoViewSet(viewsets.ModelViewSet):
	queryset = Producto.objects.all().order_by('nombre')
	serializer_class = ProductoSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		stock_bajo = self.request.query_params.get('stock_bajo')
		if stock_bajo and stock_bajo.lower() == 'true':
			return queryset.filter(stock_actual__lte=F('stock_minimo'))
		activo = self.request.query_params.get('activo')
		if activo and activo.lower() == 'true':
			return queryset.filter(activo=True)
		return queryset

	@action(detail=False, methods=['get'], url_path='bajo-stock')
	def bajo_stock(self, request):
		queryset = self.get_queryset().filter(stock_actual__lte=F('stock_minimo'))
		return Response(self.get_serializer(queryset, many=True).data)


class IngresoMercaderiaViewSet(viewsets.ModelViewSet):
	queryset = IngresoMercaderia.objects.select_related('producto', 'trabajador').order_by('-fecha', '-created_at')
	serializer_class = IngresoMercaderiaSerializer
	permission_classes = [IsAuthenticated]

	def create(self, request, *args, **kwargs):
		serializer = IngresoMercaderiaCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		ingreso = IngresoMercaderiaService().registrar_ingreso(
			{
				**serializer.validated_data,
				'fecha': timezone.localdate(),
			},
			request.user,
		)
		return Response(IngresoMercaderiaSerializer(ingreso).data, status=status.HTTP_201_CREATED)


class VentaMarketViewSet(viewsets.ModelViewSet):
	queryset = VentaMarket.objects.select_related('trabajador', 'checkin_vinculado').prefetch_related('detalles', 'detalles__producto').order_by('-fecha', '-hora')
	serializer_class = VentaMarketSerializer
	permission_classes = [IsAuthenticated]

	def get_queryset(self):
		queryset = super().get_queryset()
		fecha = self.request.query_params.get('fecha')
		producto_id = self.request.query_params.get('producto_id')
		if fecha:
			queryset = queryset.filter(fecha=fecha)
		if producto_id:
			queryset = queryset.filter(detalles__producto_id=producto_id).distinct()
		return queryset

	def create(self, request, *args, **kwargs):
		serializer = VentaMarketCreateSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		detalles = data.pop('detalles')
		venta_data = {
			'tipo_venta': data['tipo_venta'],
			'metodo_pago': data['metodo_pago'],
			'fecha': timezone.localdate(),
			'hora': timezone.localtime().time(),
		}
		if data.get('checkin_vinculado_id'):
			venta_data['checkin_vinculado_id'] = data['checkin_vinculado_id']
		venta = VentaMarketService().registrar_venta_con_stock(venta_data, detalles, request.user)
		return Response(_serializar_venta(venta), status=status.HTTP_201_CREATED)


class HealthMarketView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response({'module': 'market', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo market sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas pueden añadirse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una única responsabilidad clara.
# D - Dependency Inversion: depende de DRF y no de persistencia directa.
# ════════════════════════════════════════

# Create your views here.
