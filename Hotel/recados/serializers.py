from core.base_serializers import BaseSerializer
from recados.models import Recado


class RecadoSerializer(BaseSerializer):
    class Meta:
        model = Recado
        fields = '__all__'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define la serialización del módulo recados.
# O - Open/Closed: nuevos serializers se agregan sin alterar esta base.
# L - Liskov Substitution: el serializer hijo funciona como ModelSerializer estándar.
# I - Interface Segregation: expone una única representación del recado.
# D - Dependency Inversion: la API depende de BaseSerializer y no del ORM.
# ════════════════════════════════════════
