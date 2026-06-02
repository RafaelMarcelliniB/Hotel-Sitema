from django.urls import path

from recados.views import HealthRecadosView, RecadoViewSet

urlpatterns = [
	path('', RecadoViewSet.as_view({'get': 'list', 'post': 'create'}), name='recados-list'),
	path('<int:pk>/', RecadoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='recados-detail'),
	path('<int:pk>/leer/', RecadoViewSet.as_view({'patch': 'marcar_leido'}), name='recados-leer'),
	path('health/', HealthRecadosView.as_view(), name='recados-health'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo recados.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
