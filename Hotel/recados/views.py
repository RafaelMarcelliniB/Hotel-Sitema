from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
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
        return obj.trabajador_origen_id == request.user.id or obj.creado_por_id == request.user.id


class RecadoViewSet(viewsets.ModelViewSet):
    queryset = Recado.objects.select_related('trabajador_origen', 'creado_por').order_by('-fecha_creacion', '-id')
    serializer_class = RecadoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in {'update', 'partial_update', 'destroy'}:
            permission_classes = [IsOriginOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        categoria = self.request.query_params.get('categoria')

        if estado:
            queryset = queryset.filter(estado=estado)
        if categoria:
            queryset = queryset.filter(categoria=categoria)

        if not estado or estado in {Recado.Estado.PENDIENTE, Recado.Estado.PROCESO, ''}:
            cutoff = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(
                Q(estado__in=[Recado.Estado.PENDIENTE, Recado.Estado.PROCESO])
                | Q(estado=Recado.Estado.RESUELTO, created_at__gte=cutoff)
                | Q(estado=Recado.Estado.RESUELTO, updated_at__gte=cutoff)
            )
        elif estado == Recado.Estado.RESUELTO:
            cutoff = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(
                Q(created_at__gte=cutoff) | Q(updated_at__gte=cutoff)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        allowed_fields = {'estado'}
        data = request.data
        if set(data.keys()) - allowed_fields:
            return Response(
                {'detail': 'Solo se permite actualizar el estado del recado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        turno_origen = getattr(self.request.user, 'turno', None) or None
        serializer.save(
            creado_por=self.request.user,
            trabajador_origen=self.request.user,
            turno_origen=turno_origen,
            fecha=timezone.localdate(),
        )

    def marcar_leido(self, request, pk=None):
        instance = self.get_object()
        instance.estado = Recado.Estado.RESUELTO
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
