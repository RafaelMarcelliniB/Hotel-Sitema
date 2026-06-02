from django.urls import path

from market.views import HealthMarketView, IngresoMercaderiaViewSet, ProductoViewSet, VentaMarketViewSet

urlpatterns = [
	path('productos/', ProductoViewSet.as_view({'get': 'list', 'post': 'create'}), name='productos-list'),
	path('productos/<int:pk>/', ProductoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='productos-detail'),
	path('productos/bajo-stock/', ProductoViewSet.as_view({'get': 'bajo_stock'}), name='productos-bajo-stock'),
	path('ingreso-mercaderia/', IngresoMercaderiaViewSet.as_view({'get': 'list', 'post': 'create'}), name='ingreso-mercaderia'),
	path('ingreso-mercaderia/<int:pk>/', IngresoMercaderiaViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='ingreso-mercaderia-detail'),
	path('ventas/', VentaMarketViewSet.as_view({'get': 'list', 'post': 'create'}), name='ventas-list'),
	path('ventas/<int:pk>/', VentaMarketViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='ventas-detail'),
	path('health/', HealthMarketView.as_view(), name='market-health'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo market.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
