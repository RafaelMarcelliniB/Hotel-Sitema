from django.db import transaction
from django.utils import timezone
from core.base_services import BaseService
from cochera.repositories import EspacioCocheraRepository, RegistroVehiculoRepository
from cochera.models import EspacioCochera


class EspacioCocheraService(BaseService):
    repository_class = EspacioCocheraRepository


class RegistroVehiculoService(BaseService):
    repository_class = RegistroVehiculoRepository

    def __init__(self):
        super().__init__()
        self.espacio_repo = EspacioCocheraRepository()

    @transaction.atomic
    def registrar_ingreso(self, vehiculo_data):
        
        espacio_id = vehiculo_data.get('espacio')
        espacio = self.espacio_repo.get_by_id(espacio_id)

        if espacio.estado != EspacioCochera.Estado.LIBRE:
            raise ValueError(f"El espacio {espacio.numero} ya está ocupado.")

        #Crea el registro de entrada
        registro = self.repository.create(**vehiculo_data)

        #Actualiza estado del espacio
        self.espacio_repo.update(espacio.id, estado=EspacioCochera.Estado.OCUPADO)
        
        return registro

    @transaction.atomic
    def registrar_salida(self, registro_id, monto_total=0):
        
        registro = self.repository.get_by_id(registro_id)
        
        if registro.fecha_salida:
            raise ValueError("Este vehículo ya registró su salida.")

        #Actualiza datos de salida en el registro
        self.repository.update(
            registro.id,
            fecha_salida=timezone.now().date(),
            hora_salida=timezone.now().time(),
            monto_total=monto_total
        )

        #Libera el espacio de cochera
        self.espacio_repo.update(registro.espacio.id, estado=EspacioCochera.Estado.LIBRE)
        
        return registro
    
    
# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio de cochera.
# O - Open/Closed: nuevos casos de uso se agregan con nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos sustituyen a BaseService sin romper.
# I - Interface Segregation: cada servicio cubre una responsabilidad concreta.
# D - Dependency Inversion: la vista depende de servicios, no del ORM.
# ════════════════════════════════════════
