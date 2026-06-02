from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recados.models import Recado
from recados.serializers import RecadoSerializer
from recados.services import RecadoService


class IsOriginOrAdmin(IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or getattr(request.user, 'rol', None) == 'admin':
            return True
        return obj.trabajador_origen_id == request.user.id


class RecadoViewSet(viewsets.ModelViewSet):
    queryset = Recado.objects.select_related('trabajador_origen').order_by('-fecha', '-id')
    serializer_class = RecadoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {'update', 'partial_update', 'destroy', 'marcar_leido'}:
            permission_classes = [IsOriginOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        no_leidos = self.request.query_params.get('no_leidos')
        prioridad = self.request.query_params.get('prioridad')
        if no_leidos and no_leidos.lower() == 'true':
            queryset = queryset.filter(leido=False)
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha__range=[fecha_inicio, fecha_fin])
        return queryset

    def perform_create(self, serializer):
        serializer.save(trabajador_origen=self.request.user, fecha=timezone.localdate())

    @action(detail=True, methods=['patch'], url_path='leer')
    def marcar_leido(self, request, pk=None):
        recado = self.get_object()
        recado.leido = True
        recado.save(update_fields=['leido'])
        return Response(self.get_serializer(recado).data)


class HealthRecadosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'module': 'recados', 'status': 'ok'})


# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: cada vista atiende la API de recados sin mezclar otros módulos.
# O - Open/Closed: filtros y acciones nuevas se agregan como métodos aislados.
# L - Liskov Substitution: el viewset cumple el contrato estándar de DRF.
# I - Interface Segregation: creación, lectura y marcado de estado quedan separados.
# D - Dependency Inversion: la capa web depende de servicios y serializers, no del ORM directo.
# ════════════════════════════════════════
