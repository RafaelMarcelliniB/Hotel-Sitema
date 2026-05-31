from core.base_services import BaseService
from users.repositories import AuditLogRepository, TrabajadorRepository


class TrabajadorService(BaseService):
    repository_class = TrabajadorRepository


class AuditLogService(BaseService):
    repository_class = AuditLogRepository

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra la lógica de negocio del módulo users.
# O - Open/Closed: nuevos casos de uso se agregan mediante nuevas clases hijas.
# L - Liskov Substitution: los servicios hijos pueden reemplazar a BaseService sin romper el flujo.
# I - Interface Segregation: cada servicio cubre un caso de uso concreto y no mezcla responsabilidades.
# D - Dependency Inversion: la capa de vista depende de servicios y no de modelos ni QuerySets.
# ════════════════════════════════════════
