from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recados.models import Recado
from recados.serializers import RecadoSerializer


class RecadoListView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = RecadoSerializer
	queryset = Recado.objects.all().order_by('-fecha', '-id')


class HealthRecadosView(APIView):
	def get(self, request):
		return Response({'module': 'recados', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo recados sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas pueden añadirse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una superficie mínima y clara.
# D - Dependency Inversion: depende de DRF y no del ORM directo.
# ════════════════════════════════════════

# Create your views here.
