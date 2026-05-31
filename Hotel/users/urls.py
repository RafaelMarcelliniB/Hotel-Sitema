from django.urls import path

from users.views import CurrentUserView, HealthUsersView, LoginView

urlpatterns = [
	path('auth/login/', LoginView.as_view(), name='auth-login'),
	path('auth/me/', CurrentUserView.as_view(), name='auth-me'),
	path('health/', HealthUsersView.as_view(), name='users-health'),
]

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define únicamente el mapa de rutas del módulo users.
# O - Open/Closed: nuevas rutas se agregan sin modificar la estructura de la capa superior.
# L - Liskov Substitution: el archivo cumple el contrato esperado por Django para URLConfs.
# I - Interface Segregation: no mezcla serialización, negocio ni persistencia con el enrutamiento.
# D - Dependency Inversion: la configuración consume este URLConf como abstracción del módulo.
# ════════════════════════════════════════
