class BaseService:
    repository_class = None

    def __init__(self):
        if self.repository_class is None:
            raise NotImplementedError('repository_class must be defined in subclasses')
        self.repository = self.repository_class()

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define el contrato común de servicios de negocio.
# O - Open/Closed: cada servicio de dominio extiende esta base sin cambiarla.
# L - Liskov Substitution: un servicio hijo puede reemplazar a BaseService sin romper el flujo.
# I - Interface Segregation: solo obliga a inyectar un repositorio, sin mezclar detalles de API o modelo.
# D - Dependency Inversion: la lógica de negocio depende de repositorios abstraídos y no de QuerySets directos.
# ════════════════════════════════════════
