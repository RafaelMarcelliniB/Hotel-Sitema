from django.db import models


class BaseRepository:
    model = None

    def __init__(self):
        if self.model is None:
            raise NotImplementedError('model must be defined in subclasses')

    def get_by_id(self, object_id):
        return self.model.objects.get(pk=object_id)

    def get_all(self):
        return self.model.objects.all()

    def create(self, **data):
        return self.model.objects.create(**data)

    def update(self, object_id, **data):
        instance = self.get_by_id(object_id)
        for field, value in data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def delete(self, object_id):
        instance = self.get_by_id(object_id)
        instance.delete()
        return True

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: concentra operaciones CRUD genéricas sobre persistencia.
# O - Open/Closed: repositorios concretos extienden esta base para nuevos modelos sin tocarla.
# L - Liskov Substitution: cualquier repositorio hijo puede sustituir a BaseRepository manteniendo el contrato CRUD.
# I - Interface Segregation: expone solo operaciones genéricas necesarias para acceso a datos.
# D - Dependency Inversion: los servicios dependen de esta abstracción y no del ORM directamente.
# ════════════════════════════════════════
