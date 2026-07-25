from django.urls import path

from hotel.views import (
	CheckInActiveListView,
	CheckInCargoAdicionalView,
	CheckInCreateView,
	CheckInDetailView,
	CheckOutCreateView,
	HabitacionViewSet,
	HealthHotelView,
	HuespedViewSet,
	ReservaViewSet,
)

urlpatterns = [
	path('habitaciones/', HabitacionViewSet.as_view({'get': 'list', 'post': 'create'}), name='habitaciones-list'),
	path('habitaciones/disponibles/', HabitacionViewSet.as_view({'get': 'disponibles'}), name='habitaciones-disponibles'),
	path('habitaciones/<int:pk>/', HabitacionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='habitaciones-detail'),
	path('habitaciones/<int:pk>/estado/', HabitacionViewSet.as_view({'patch': 'estado'}), name='habitaciones-estado'),
	path('habitaciones/<int:pk>/limpiar/', HabitacionViewSet.as_view({'post': 'limpiar'}), name='habitaciones-limpiar'),
	path('habitaciones/<int:pk>/bloquear/', HabitacionViewSet.as_view({'post': 'bloquear'}), name='habitaciones-bloquear'),
	path('huespedes/', HuespedViewSet.as_view({'get': 'list', 'post': 'create'}), name='huespedes-list'),
	path('huespedes/<int:pk>/', HuespedViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='huespedes-detail'),
	path('reservas/', ReservaViewSet.as_view({'get': 'list', 'post': 'create'}), name='reservas-list'),
	path('reservas/<int:pk>/', ReservaViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='reservas-detail'),
	path('reservas/vencidas/', ReservaViewSet.as_view({'get': 'vencidas'}), name='reservas-vencidas'),
	path('reservas/<int:pk>/checkin/', ReservaViewSet.as_view({'post': 'checkin'}), name='reservas-checkin'),
	path('checkin/', CheckInCreateView.as_view(), name='checkin-create'),
	path('checkin/activos/', CheckInActiveListView.as_view(), name='checkin-activos'),
	path('checkin/<int:checkin_id>/', CheckInDetailView.as_view(), name='checkin-detail'),
	path('checkin/<int:checkin_id>/cargo-adicional/', CheckInCargoAdicionalView.as_view(), name='checkin-cargo-adicional'),
	path('checkout/<int:checkin_id>/', CheckOutCreateView.as_view(), name='checkout-create'),
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
