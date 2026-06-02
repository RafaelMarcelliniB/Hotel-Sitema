from django.urls import path

from cochera.views import (
	EspacioCocheraDisponiblesView,
	EspacioCocheraViewSet,
	HealthCocheraView,
	RegistroVehiculoHistorialView,
	RegistroVehiculoIngresoView,
	RegistroVehiculoSalidaView,
)

urlpatterns = [
	path('espacios/', EspacioCocheraViewSet.as_view({'get': 'list', 'post': 'create'}), name='espacios-list'),
	path('espacios/<int:pk>/', EspacioCocheraViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='espacios-detail'),
	path('espacios/disponibles/', EspacioCocheraDisponiblesView.as_view(), name='espacios-disponibles'),
	path('vehiculos/ingreso/', RegistroVehiculoIngresoView.as_view(), name='vehiculos-ingreso'),
	path('vehiculos/<int:registro_id>/salida/', RegistroVehiculoSalidaView.as_view(), name='vehiculos-salida'),
	path('registros/', RegistroVehiculoHistorialView.as_view(), name='registros-historial'),
	path('health/', HealthCocheraView.as_view(), name='cochera-health'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo cochera.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
