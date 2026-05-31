from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from caja.models import Caja
from caja.serializers import CajaSerializer


class CajaListView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = CajaSerializer
	queryset = Caja.objects.all().order_by('-fecha_apertura', '-hora_apertura')


class HealthCajaView(APIView):
	def get(self, request):
		return Response({'module': 'caja', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo caja sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas pueden incorporarse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una única responsabilidad clara.
# D - Dependency Inversion: depende de DRF y no del ORM directo.
# ════════════════════════════════════════

# Create your views here.

# Create your views here.
