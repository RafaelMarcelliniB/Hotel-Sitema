from django.urls import path

from caja.views import (
	CajaAperturaView,
	CajaCierreView,
	CajaListView,
	CajaResumenView,
 	DashboardStatsView,
	HealthCajaView,
	MovimientoCajaPagarDeudaView,
	MovimientoCajaViewSet,
    CajaReporteExcelView,
)

urlpatterns = [
	path('cajas/', CajaListView.as_view(), name='cajas-list'),
	path('apertura/', CajaAperturaView.as_view(), name='caja-apertura'),
	path('cierre/', CajaCierreView.as_view(), name='caja-cierre'),
	path('resumen/', CajaResumenView.as_view(), name='caja-resumen'),
	path('dashboard/', DashboardStatsView.as_view(), name='caja-dashboard'),
	path('movimientos/', MovimientoCajaViewSet.as_view({'get': 'list', 'post': 'create'}), name='movimientos-list'),
	path('movimientos/<int:pk>/', MovimientoCajaViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='movimientos-detail'),
	path('movimientos/<int:movimiento_id>/pagar-deuda/', MovimientoCajaPagarDeudaView.as_view(), name='movimientos-pagar-deuda'),
	path('health/', HealthCajaView.as_view(), name='caja-health'),
    path('<int:caja_id>/reporte-excel/', CajaReporteExcelView.as_view(), name='caja-reporte-excel'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo caja.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
