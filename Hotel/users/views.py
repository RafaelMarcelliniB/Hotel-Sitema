from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import AuditLog, Trabajador
from users.serializers import AuditLogSerializer, TrabajadorSerializer, TrabajadorWriteSerializer


class IsAdminOrSelf(IsAuthenticated):
	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser or request.user.rol == Trabajador.Rol.ADMIN:
			return True
		return obj.pk == request.user.pk


class TrabajadorViewSet(viewsets.ModelViewSet):
	queryset = Trabajador.objects.all().order_by('id')
	permission_classes = [IsAuthenticated]

	def get_permissions(self):
		if self.action in {'list', 'create', 'destroy', 'cambiar_password', 'toggle_activo', 'por_turno'}:
			permission_classes = [IsAdminUser]
		elif self.action in {'retrieve', 'update', 'partial_update'}:
			permission_classes = [IsAdminOrSelf]
		else:
			permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]

	def get_serializer_class(self):
		if self.action in {'create', 'update', 'partial_update'}:
			return TrabajadorWriteSerializer
		return TrabajadorSerializer

	def perform_create(self, serializer):
		trabajador = serializer.save()
		AuditLog.objects.create(
			trabajador=self.request.user,
			accion='crear_trabajador',
			modulo='users',
			detalle=f'Creó trabajador {trabajador.username}',
		)

	def perform_update(self, serializer):
		trabajador = serializer.save()
		AuditLog.objects.create(
			trabajador=self.request.user,
			accion='actualizar_trabajador',
			modulo='users',
			detalle=f'Actualizó trabajador {trabajador.username}',
		)

	def perform_destroy(self, instance):
		AuditLog.objects.create(
			trabajador=self.request.user,
			accion='eliminar_trabajador',
			modulo='users',
			detalle=f'Eliminó trabajador {instance.username}',
		)
		instance.delete()

	@action(detail=True, methods=['post'], url_path='cambiar-password')
	def cambiar_password(self, request, pk=None):
		trabajador = self.get_object()
		nueva_password = request.data.get('nueva_password')
		if not nueva_password:
			return Response({'detail': 'nueva_password es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)
		trabajador.set_password(nueva_password)
		trabajador.save(update_fields=['password'])
		AuditLog.objects.create(
			trabajador=request.user,
			accion='cambiar_password',
			modulo='users',
			detalle=f'Cambiò la contraseña de {trabajador.username}',
		)
		return Response({'detail': 'Contraseña actualizada correctamente'})

	@action(detail=True, methods=['patch'], url_path='toggle-activo')
	def toggle_activo(self, request, pk=None):
		trabajador = self.get_object()
		trabajador.activo = not trabajador.activo
		trabajador.save(update_fields=['activo'])
		AuditLog.objects.create(
			trabajador=request.user,
			accion='toggle_activo',
			modulo='users',
			detalle=f'Cambió estado de {trabajador.username} a {trabajador.activo}',
		)
		return Response(TrabajadorSerializer(trabajador).data)

	@action(detail=False, methods=['get'], url_path='por-turno')
	def por_turno(self, request):
		turno = request.query_params.get('turno')
		queryset = self.get_queryset()
		if turno:
			queryset = queryset.filter(turno=turno)
		return Response(TrabajadorSerializer(queryset, many=True).data)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = AuditLog.objects.all().order_by('-fecha_hora')
	serializer_class = AuditLogSerializer
	permission_classes = [IsAdminUser]

	def get_queryset(self):
		queryset = super().get_queryset()
		modulo = self.request.query_params.get('modulo')
		if modulo:
			queryset = queryset.filter(modulo=modulo)
		return queryset


class HotelTokenObtainPairSerializer(TokenObtainPairSerializer):
	def validate(self, attrs):
		data = super().validate(attrs)
		data['user'] = TrabajadorSerializer(self.user).data
		return data


class LoginView(TokenObtainPairView):
	permission_classes = [AllowAny]
	serializer_class = HotelTokenObtainPairSerializer


class CurrentUserView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response(TrabajadorSerializer(request.user).data)


class HealthUsersView(APIView):
	def get(self, request):
		return Response({'module': 'users', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo users sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas del módulo pueden agregarse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una vista mínima y no fuerza dependencias extra.
# D - Dependency Inversion: la vista depende de la abstracción de DRF y no del ORM.
# ════════════════════════════════════════

# Create your views here.
