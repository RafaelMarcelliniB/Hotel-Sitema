from django.urls import path

from market.views import (
	HealthMarketView,
	IngresoMercaderiaViewSet,
	ProductoViewSet,
	VentaMarketViewSet,
	PreviewProductosExcelView,
	ImportarProductosExcelView,
	DescargarPlantillaProductosView,
)

urlpatterns = [
	path('productos/', ProductoViewSet.as_view({'get': 'list', 'post': 'create'}), name='productos-list'),
	path('productos/bajo-stock/', ProductoViewSet.as_view({'get': 'bajo_stock'}), name='productos-bajo-stock'),
	path('productos/<int:pk>/transferir/', ProductoViewSet.as_view({'post': 'transferir_stock'}), name='productos-transferir'),
	path('productos/<int:pk>/transferencias/', ProductoViewSet.as_view({'get': 'transferencias_historial'}), name='productos-transferencias'),
	path('productos/<int:pk>/', ProductoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='productos-detail'),
	path('ingreso-mercaderia/', IngresoMercaderiaViewSet.as_view({'get': 'list', 'post': 'create'}), name='ingreso-mercaderia'),
	path('ingreso-mercaderia/<int:pk>/', IngresoMercaderiaViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='ingreso-mercaderia-detail'),
	path('ventas/', VentaMarketViewSet.as_view({'get': 'list', 'post': 'create'}), name='ventas-list'),
	path('ventas/<int:pk>/', VentaMarketViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='ventas-detail'),
	path('health/', HealthMarketView.as_view(), name='market-health'),
	path('productos/preview-excel/', PreviewProductosExcelView.as_view(), name='productos-preview-excel'),
	path('productos/importar-excel/', ImportarProductosExcelView.as_view(), name='productos-importar-excel'),
	path('productos/plantilla/<str:formato>/', DescargarPlantillaProductosView.as_view(), name='productos-descargar-plantilla'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo market.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
