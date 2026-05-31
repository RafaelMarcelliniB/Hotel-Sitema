from django.urls import path

from hotel.views import HabitacionListView, HealthHotelView, HuespedListView

urlpatterns = [
	path('habitaciones/', HabitacionListView.as_view(), name='habitaciones-list'),
	path('huespedes/', HuespedListView.as_view(), name='huespedes-list'),
	path('health/', HealthHotelView.as_view(), name='hotel-health'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo hotel.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
