from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import Producto
from market.serializers import ProductoSerializer


class ProductoListView(ListAPIView):
	permission_classes = [IsAuthenticated]
	serializer_class = ProductoSerializer
	queryset = Producto.objects.all().order_by('nombre')


class HealthMarketView(APIView):
	def get(self, request):
		return Response({'module': 'market', 'status': 'ok'})

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: responde a la API del módulo market sin mezclar reglas de negocio.
# O - Open/Closed: nuevas vistas pueden añadirse como clases separadas.
# L - Liskov Substitution: la vista cumple el contrato esperado por DRF.
# I - Interface Segregation: expone una única responsabilidad clara.
# D - Dependency Inversion: depende de DRF y no de persistencia directa.
# ════════════════════════════════════════

# Create your views here.
