from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hotel.models import Habitacion, Huesped
from hotel.serializers import HabitacionSerializer, HuespedSerializer


class HabitacionListView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = HabitacionSerializer
	queryset = Habitacion.objects.all().order_by('numero')


class HuespedListView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = HuespedSerializer
	queryset = Huesped.objects.all().order_by('apellido', 'nombre')


class HealthHotelView(APIView):
	def get(self, request):
		return Response({'module': 'hotel', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo hotel sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas se incorporan como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una superficie mínima y clara.
# D - Dependency Inversion: la capa web depende de DRF y no del ORM directo.
# ════════════════════════════════════════

# Create your views here.
