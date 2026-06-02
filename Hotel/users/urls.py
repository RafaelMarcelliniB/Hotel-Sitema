from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import AuditLogViewSet, CurrentUserView, HealthUsersView, LoginView, TrabajadorViewSet


router = DefaultRouter()
router.register(r'trabajadores', TrabajadorViewSet, basename='trabajadores')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
	path('', include(router.urls)),
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
