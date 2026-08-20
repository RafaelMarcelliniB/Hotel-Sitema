from django.db.models import F
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
import traceback

from caja.permissions import CajaAbertaPermission
from market.models import IngresoMercaderia, Producto, VentaMarket, Categoria
from market.serializers import (
	IngresoMercaderiaCreateSerializer,
	IngresoMercaderiaSerializer,
	ProductoSerializer,
	VentaMarketCreateSerializer,
	VentaMarketSerializer,
)
from market.services import IngresoMercaderiaService, VentaMarketService, ProductoService
import pandas as pd
from decimal import Decimal, InvalidOperation
from io import BytesIO
from django.http import HttpResponse
import unicodedata



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
				'ubicacion_stock': detalle.ubicacion_stock,
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
			return queryset.annotate(
				stock_total_calculado=F('stock_almacen') + F('stock_recepcion') + F('stock_refrigeradora'),
			).filter(stock_total_calculado__lte=F('stock_minimo'))
		activo = self.request.query_params.get('activo')
		if activo and activo.lower() == 'true':
			return queryset.filter(activo=True)
		return queryset

	@action(detail=False, methods=['get'], url_path='bajo-stock')
	def bajo_stock(self, request):
		queryset = self.get_queryset().annotate(
			stock_total_calculado=F('stock_almacen') + F('stock_recepcion') + F('stock_refrigeradora'),
		).filter(stock_total_calculado__lte=F('stock_minimo'))
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
	permission_classes = [IsAuthenticated, CajaAbertaPermission]

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
		
		try:
			# Ejecuta el flujo lógico que valida stock y caja activa
			venta = VentaMarketService().registrar_venta_con_stock(venta_data, detalles, request.user)
			return Response(_serializar_venta(venta), status=status.HTTP_201_CREATED)
		
		except ValueError as e:
			# Captura el error de "No se puede registrar una venta si el trabajador no cuenta con una caja abierta..."
			return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
		
		except Exception as e:
			# Muestra la traza exacta en tu consola de Django si ocurre un error 500 inesperado
			print("=== ERROR 500 EN VENTAMARKETVIEWSET ===")
			traceback.print_exc()
			print("========================================")
			return Response({'detail': f'Error interno en el servidor: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthMarketView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response({'module': 'market', 'status': 'ok'})


class IsAdminTrabajadorPermission(BasePermission):
	message = 'Se requieren privilegios de administrador.'

	def has_permission(self, request, view):
		user = getattr(request, 'user', None)
		if not user or not user.is_authenticated:
			return False
		# Aceptar superuser o rol admin/administrador (tolerancia en mayúsculas)
		rol = getattr(user, 'rol', '') or ''
		return bool(user.is_superuser or rol.lower() in ('admin', 'administrador'))


class PreviewProductosExcelView(APIView):
	"""Recibe un archivo xlsx o csv y devuelve una previsualización de las primeras filas."""
	permission_classes = [IsAuthenticated, IsAdminTrabajadorPermission]

	def post(self, request):
		f = request.FILES.get('file')
		if not f:
			return Response({'detail': 'Archivo no provisto'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			if f.name.lower().endswith('.csv'):
				df = pd.read_csv(f)
			else:
				df = pd.read_excel(f, engine='openpyxl')
		except Exception as e:
			return Response({'detail': f'Error al leer el archivo: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

		# Normalizar nombres de columnas para búsqueda robusta
		def _norm(col):
			if not isinstance(col, str):
				return ''
			col = col.strip()
			col = unicodedata.normalize('NFKD', col)
			col = col.encode('ascii', 'ignore').decode('ascii')
			col = col.lower()
			col = ''.join(ch for ch in col if ch.isalnum())
			return col

		col_map = { _norm(c): c for c in df.columns }

		expected = ['Nombre', 'Categoria', 'Precio Unitario', 'Stock Almacen', 'Stock Recepcion', 'Stock Refrigeradora', 'Stock Minimo', 'Activo']
		rows = []
		for idx, raw_row in df.head(20).iterrows():
			row = raw_row.fillna('')
			def val(label):
				key = _norm(label)
				orig = col_map.get(key)
				if orig is None:
					return ''
				return row.get(orig, '')

			rows.append({
				'fila': int(idx) + 2,
				'Nombre': str(val('Nombre')),
				'Categoria': str(val('Categoria')),
				'Precio Unitario': str(val('Precio Unitario')),
				'Stock Almacen': str(val('Stock Almacen')),
				'Stock Recepcion': str(val('Stock Recepcion')),
				'Stock Refrigeradora': str(val('Stock Refrigeradora')),
				'Stock Minimo': str(val('Stock Minimo')),
				'Activo': str(val('Activo')),
			})

		return Response({'preview': rows})


class ImportarProductosExcelView(APIView):
	"""Importa productos desde Excel o CSV. Solo administradores."""
	permission_classes = [IsAuthenticated, IsAdminTrabajadorPermission]

	def post(self, request):
		f = request.FILES.get('file')
		if not f:
			return Response({'detail': 'Archivo no provisto'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			if f.name.lower().endswith('.csv'):
				df = pd.read_csv(f)
			else:
				df = pd.read_excel(f, engine='openpyxl')
		except Exception as e:
			return Response({'detail': f'Error al leer el archivo: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

		created = 0
		updated = 0
		errors = []

		# Normalización de columnas
		def _norm(col):
			if not isinstance(col, str):
				return ''
			col = col.strip()
			col = unicodedata.normalize('NFKD', col)
			col = col.encode('ascii', 'ignore').decode('ascii')
			col = col.lower()
			col = ''.join(ch for ch in col if ch.isalnum())
			return col

		col_map = { _norm(c): c for c in df.columns }

		# también mapa de etiquetas -> valor para categorias (labels de choices)
		categoria_map = { _norm(label): value for (value, label) in Producto._meta.get_field('categoria').choices }

		for idx, raw_row in df.iterrows():
			fila = int(idx) + 2
			row = raw_row.fillna('')
			try:
				# helper para obtener valor por etiqueta esperada
				def val(label):
					key = _norm(label)
					orig = col_map.get(key)
					if orig is None:
						return ''
					return row.get(orig, '')

				nombre = str(val('Nombre')).strip()
				if not nombre:
					raise ValueError('Nombre obligatorio')

				# Categoria: buscar en choices por label, si no existe usar el texto en mayúsculas (crea categoría implícita)
				categoria_raw = str(val('Categoria')).strip()
				categoria_key = _norm(categoria_raw)
				if categoria_raw:
					categoria = categoria_map.get(categoria_key)
					if not categoria:
						# intentar usar valor directo (por si el CSV contiene el código)
						if categoria_raw.upper() in [c for (c, _) in Producto._meta.get_field('categoria').choices]:
							categoria = categoria_raw.upper()
						else:
							# usar texto recibido como valor, truncando a 30 chars
							categoria = categoria_raw.upper()[:30]
				else:
					categoria = None

				if not categoria:
					raise ValueError(f'Categoria inválida o vacía: {categoria_raw}')

				# Precio
				precio_raw = val('Precio Unitario')
				try:
					precio_unitario = Decimal(str(precio_raw)) if precio_raw != '' else Decimal('0')
				except (InvalidOperation, TypeError):
					raise ValueError(f'Precio Unitario inválido: {precio_raw}')

				def stock_value(label):
					raw_value = val(label)
					try:
						value = int(raw_value) if raw_value != '' else 0
					except Exception:
						raise ValueError(f'{label} inválido: {raw_value}')
					if value < 0:
						raise ValueError(f'{label} no puede ser negativo')
					return value

				stock_almacen = stock_value('Stock Almacen')
				stock_recepcion = stock_value('Stock Recepcion')
				stock_refrigeradora = stock_value('Stock Refrigeradora')

				# Stock minimo
				stock_minimo_raw = val('Stock Minimo')
				stock_minimo = 0
				if stock_minimo_raw != '':
					try:
						stock_minimo = int(stock_minimo_raw)
					except Exception:
						raise ValueError(f'Stock Minimo inválido: {stock_minimo_raw}')

				# Activo
				activo_raw = str(val('Activo')).strip().lower()
				if activo_raw in ['false', 'no', '0', 'n']:
					activo = False
				elif activo_raw in ['true', 'si', '1', 's']:
					activo = True
				elif activo_raw == '':
					activo = True
				else:
					activo = True

				producto, created_flag = Producto.objects.get_or_create(nombre=nombre, defaults={
					'categoria': categoria,
					'precio_unitario': precio_unitario,
					'stock_almacen': stock_almacen,
					'stock_recepcion': stock_recepcion,
					'stock_refrigeradora': stock_refrigeradora,
					'stock_minimo': stock_minimo,
					'activo': activo,
				})

				if created_flag:
					created += 1
				else:
					# Actualizar campos relevantes
					producto.categoria = categoria
					producto.precio_unitario = precio_unitario
					producto.stock_almacen = stock_almacen
					producto.stock_recepcion = stock_recepcion
					producto.stock_refrigeradora = stock_refrigeradora
					producto.stock_minimo = stock_minimo
					producto.activo = activo
					producto.save()
					updated += 1

			except Exception as e:
				errors.append({'fila': fila, 'error': str(e)})

		return Response({'created': created, 'updated': updated, 'errors': errors})


class DescargarPlantillaProductosView(APIView):
    """Entrega al cliente una plantilla de ejemplo en .xlsx o .csv.

    Ambos formatos contienen exactamente las mismas cabeceras/columnas
    para que el importador las procese de forma idéntica.

    Ruta esperada: /market/productos/plantilla/<format>/  donde
    <format> es 'xlsx' o 'csv'.
    """
    permission_classes = [IsAuthenticated, IsAdminTrabajadorPermission]

    def get(self, request, formato=None):
        required_headers = [
			'Nombre', 'Categoria', 'Precio Unitario', 'Stock Almacen',
			'Stock Recepcion', 'Stock Refrigeradora', 'Stock Minimo', 'Activo'
        ]

        # DataFrame vacío con las columnas en el orden esperado
        df = pd.DataFrame(columns=required_headers)

        formato = (formato or '').lower()
        if formato == 'xlsx':
            buf = BytesIO()
            # to_excel genera un archivo Excel con las mismas columnas
            df.to_excel(buf, index=False, engine='openpyxl')
            buf.seek(0)
            resp = HttpResponse(
                buf.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            resp['Content-Disposition'] = 'attachment; filename="plantilla_productos.xlsx"'
            return resp

        elif formato == 'csv':
            # csv con BOM UTF-8 para compatibilidad con Excel en Windows
            csv_text = df.to_csv(index=False, encoding='utf-8-sig')
            resp = HttpResponse(csv_text, content_type='text/csv; charset=utf-8')
            resp['Content-Disposition'] = 'attachment; filename="plantilla_productos.csv"'
            return resp

        else:
            return Response({'detail': 'Formato no soportado. Use "xlsx" o "csv".'}, status=status.HTTP_400_BAD_REQUEST)

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo market sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas pueden añadirse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una única responsabilidad clara.
# D - Dependency Inversion: depende de DRF y no de persistencia directa.
# ════════════════════════════════════════

# Create your views here.
