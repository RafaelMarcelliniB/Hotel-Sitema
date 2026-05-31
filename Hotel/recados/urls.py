from django.urls import path

from recados.views import HealthRecadosView, RecadoListView

urlpatterns = [
	path('', RecadoListView.as_view(), name='recados-list'),
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
