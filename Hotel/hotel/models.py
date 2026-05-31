from django.conf import settings
from django.db import models

from core.base_models import BaseModel


class Habitacion(BaseModel):
	class Tipo(models.TextChoices):
		SIMPLE = 'SIMPLE', 'Simple'
		DOBLE = 'DOBLE', 'Doble'
		SUITE = 'SUITE', 'Suite'
		MATRI = 'MATRI', 'Matri'
		MATRI_VIP = 'MATRI_VIP', 'Matri Vip'
		BLUE = 'BLUE', 'Blue'
		RED = 'RED', 'Red'
		TRIPLE = 'TRIPLE', 'Triple'
		CAFETIN = 'CAFETIN', 'Cafetín'

	class MarcaTV(models.TextChoices):
		JVC = 'JVC', 'JVC'
		JVC_V = 'JVC_V', 'JVC V'
		HISENSE = 'HISENSE', 'Hisense'
		SM = 'SM', 'SM'

	class TipoCama(models.TextChoices):
		DOS_PLAZAS = 'DOS_PLAZAS', 'Dos Plazas'
		QUEEN = 'QUEEN', 'Queen'
		KING = 'KING', 'King'

	class EstadoOcupacion(models.TextChoices):
		DISPONIBLE = 'DISPONIBLE', 'Disponible'
		OCUPADO = 'OCUPADO', 'Ocupado'
		RESERVADO = 'RESERVADO', 'Reservado'
		BLOQUEADO = 'BLOQUEADO', 'Bloqueado'

	class EstadoLimpieza(models.TextChoices):
		LIMPIO = 'LIMPIO', 'Limpio'
		SUCIO = 'SUCIO', 'Sucio'

	numero = models.CharField(max_length=20, unique=True)
	piso = models.PositiveIntegerField()
	tipo = models.CharField(max_length=20, choices=Tipo.choices)
	marca_tv = models.CharField(max_length=20, choices=MarcaTV.choices)
	tipo_cama = models.CharField(max_length=20, choices=TipoCama.choices)
	estado_ocupacion = models.CharField(max_length=20, choices=EstadoOcupacion.choices, default=EstadoOcupacion.DISPONIBLE)
	estado_limpieza = models.CharField(max_length=20, choices=EstadoLimpieza.choices, default=EstadoLimpieza.LIMPIO)
	tarifa_dia = models.DecimalField(max_digits=10, decimal_places=2)
	tarifa_noche = models.DecimalField(max_digits=10, decimal_places=2)
	tarifa_madrugada = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self) -> str:
		return f'Habitación {self.numero}'


class Huesped(BaseModel):
	class Nacionalidad(models.TextChoices):
		PERU = 'PERU', 'Peru'
		EXTRANJERO = 'EXTRANJERO', 'Extranjero'

	class EstadoCivil(models.TextChoices):
		SOLTERO = 'SOLTERO', 'Soltero'
		PAREJA = 'PAREJA', 'Pareja'
		CASADO = 'CASADO', 'Casado'

	class TipoVisita(models.TextChoices):
		INDEPENDIENTE = 'INDEPENDIENTE', 'Independiente'
		VIAJERO = 'VIAJERO', 'Viajero'
		TURISTA = 'TURISTA', 'Turista'

	nombre = models.CharField(max_length=100)
	apellido = models.CharField(max_length=100)
	dni_pasaporte = models.CharField(max_length=30, unique=True)
	telefono = models.CharField(max_length=30, blank=True)
	ciudad_origen = models.CharField(max_length=100, blank=True)
	nacionalidad = models.CharField(max_length=20, choices=Nacionalidad.choices)
	estado_civil = models.CharField(max_length=20, choices=EstadoCivil.choices)
	tipo_visita = models.CharField(max_length=20, choices=TipoVisita.choices)

	def __str__(self) -> str:
		return f'{self.nombre} {self.apellido}'


class CheckIn(BaseModel):
	class TurnoIngreso(models.TextChoices):
		DIA = 'DIA', 'Día'
		NOCHE = 'NOCHE', 'Noche'
		MADRUGADA = 'MADRUGADA', 'Madrugada'

	class TipoPago(models.TextChoices):
		EFECTIVO = 'EFECTIVO', 'Efectivo'
		YAPE = 'YAPE', 'Yape'
		TARJETA = 'TARJETA', 'Tarjeta'

	class Estado(models.TextChoices):
		ACTIVO = 'ACTIVO', 'Activo'
		CERRADO = 'CERRADO', 'Cerrado'
		RESERVA = 'RESERVA', 'Reserva'

	habitacion = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name='checkins')
	huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT, related_name='checkins')
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='checkins')
	fecha_entrada = models.DateField()
	hora_entrada = models.TimeField()
	fecha_salida_estimada = models.DateField(null=True, blank=True)
	hora_salida_estimada = models.TimeField(null=True, blank=True)
	fecha_salida_real = models.DateField(null=True, blank=True)
	hora_salida_real = models.TimeField(null=True, blank=True)
	turno_ingreso = models.CharField(max_length=20, choices=TurnoIngreso.choices)
	tipo_pago = models.CharField(max_length=20, choices=TipoPago.choices)
	monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monto_deuda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
	es_pareja = models.BooleanField(default=False)

	def __str__(self) -> str:
		return f'CheckIn {self.habitacion.numero} - {self.huesped}'


class CheckOut(BaseModel):
	class MetodoPago(models.TextChoices):
		EFECTIVO = 'EFECTIVO', 'Efectivo'
		YAPE = 'YAPE', 'Yape'
		TARJETA = 'TARJETA', 'Tarjeta'
		MIXTO = 'MIXTO', 'Mixto'

	checkin = models.OneToOneField(CheckIn, on_delete=models.CASCADE, related_name='checkout')
	trabajador_checkout = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='checkouts')
	subtotal_habitacion = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	subtotal_adicionales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	subtotal_market = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	subtotal_cochera = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total_general = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
	deuda_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)

	def __str__(self) -> str:
		return f'CheckOut {self.checkin_id}'


class CargoAdicional(BaseModel):
	checkin = models.ForeignKey(CheckIn, on_delete=models.CASCADE, related_name='cargos_adicionales')
	concepto = models.CharField(max_length=150)
	monto = models.DecimalField(max_digits=10, decimal_places=2)
	fecha = models.DateField()
	hora = models.TimeField()
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='cargos_adicionales')

	def __str__(self) -> str:
		return self.concepto


class Reserva(BaseModel):
	class Estado(models.TextChoices):
		PENDIENTE = 'PENDIENTE', 'Pendiente'
		CONFIRMADA = 'CONFIRMADA', 'Confirmada'
		CANCELADA = 'CANCELADA', 'Cancelada'
		COMPLETADA = 'COMPLETADA', 'Completada'

	class AlertaColor(models.TextChoices):
		ROJO = 'ROJO', 'Rojo'
		AMARILLO = 'AMARILLO', 'Amarillo'

	class TipoPagoAdelanto(models.TextChoices):
		EFECTIVO = 'EFECTIVO', 'Efectivo'
		YAPE = 'YAPE', 'Yape'
		TARJETA = 'TARJETA', 'Tarjeta'

	huesped = models.ForeignKey(Huesped, on_delete=models.PROTECT, related_name='reservas')
	habitacion_preferida = models.ForeignKey(Habitacion, on_delete=models.PROTECT, related_name='reservas')
	trabajador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='reservas')
	fecha_llegada_estimada = models.DateField()
	hora_llegada_estimada = models.TimeField()
	monto_adelanto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	tipo_pago_adelanto = models.CharField(max_length=20, choices=TipoPagoAdelanto.choices)
	estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
	notas = models.TextField(blank=True)
	alerta_color = models.CharField(max_length=20, choices=AlertaColor.choices, default=AlertaColor.AMARILLO)

	def __str__(self) -> str:
		return f'Reserva {self.huesped}'

# ════════════════════════════════════════
# SOLID APLICADO EN ESTE ARCHIVO:
# S - Single Responsibility: define solo las entidades de habitaciones, huéspedes, check-in, check-out, cargos y reservas.
# O - Open/Closed: nuevas variaciones de dominio se agregan con nuevas clases sin romper las existentes.
# L - Liskov Substitution: cada modelo respeta el contrato de modelo Django y puede sustituirse por su base abstracta.
# I - Interface Segregation: cada entidad tiene campos específicos de su contexto sin mezclar módulos ajenos.
# D - Dependency Inversion: los servicios y vistas dependen de estas abstracciones de dominio y no del ORM directo.
# ════════════════════════════════════════
