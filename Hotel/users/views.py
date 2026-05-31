from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import TrabajadorSerializer


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
