from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cochera.models import EspacioCochera
from cochera.serializers import EspacioCocheraSerializer


class EspacioCocheraListView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = EspacioCocheraSerializer
	queryset = EspacioCochera.objects.all().order_by('numero')


class HealthCocheraView(APIView):
	def get(self, request):
		return Response({'module': 'cochera', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo cochera sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas pueden añadirse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una superficie mínima y clara.
# D - Dependency Inversion: depende de DRF y no del ORM directo.
# ════════════════════════════════════════

# Create your views here.
