from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)
    configuracion = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return self.nombre

class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('procesando', 'Procesando'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    codigo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reserva = models.OneToOneField('reservas.Reserva', on_delete=models.CASCADE)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_procesamiento = models.DateTimeField(null=True, blank=True)
    transaccion_id = models.CharField(max_length=200, blank=True)
    respuesta_pago = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"Pago {self.codigo} - ${self.monto}"
    
    def marcar_completado(self, transaccion_id="", respuesta=None):
        """Marcar pago como completado"""
        self.estado = 'completado'
        self.fecha_procesamiento = timezone.now()
        self.transaccion_id = transaccion_id
        if respuesta:
            self.respuesta_pago = respuesta
        self.save()
        
        # Confirmar la reserva asociada
        self.reserva.confirmar()
    
    def marcar_fallido(self, respuesta=None):
        """Marcar pago como fallido"""
        self.estado = 'fallido'
        self.fecha_procesamiento = timezone.now()
        if respuesta:
            self.respuesta_pago = respuesta
        self.save()
        
        # Cancelar la reserva asociada
        self.reserva.cancelar()

class CuponDescuento(models.Model):
    TIPO_CHOICES = [
        ('porcentaje', 'Porcentaje'),
        ('monto_fijo', 'Monto Fijo'),
        ('2x1', '2x1'),
    ]
    
    codigo = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.TextField()
    uso_minimo_compra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    usos_maximos = models.IntegerField(null=True, blank=True)
    usos_realizados = models.IntegerField(default=0)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    activo = models.BooleanField(default=True)
    peliculas_aplicables = models.ManyToManyField('peliculas.Pelicula', blank=True)
    
    def __str__(self):
        return f"Cupón {self.codigo}"
    
    @property
    def vigente(self):
        """Verificar si el cupón está vigente"""
        ahora = timezone.now()
        return self.activo and self.fecha_inicio <= ahora <= self.fecha_fin
    
    @property
    def disponible(self):
        """Verificar si el cupón todavía tiene usos disponibles"""
        return self.usos_maximos is None or self.usos_realizados < self.usos_maximos
    
    def puede_usarse(self, monto_compra=0):
        """Verificar si el cupón puede ser usado"""
        return self.vigente and self.disponible and monto_compra >= self.uso_minimo_compra
    
    def calcular_descuento(self, monto_original):
        """Calcular el monto de descuento"""
        if not self.puede_usarse(monto_original):
            return 0
        
        if self.tipo == 'porcentaje':
            return monto_original * (self.valor / 100)
        elif self.tipo == 'monto_fijo':
            return min(self.valor, monto_original)
        elif self.tipo == '2x1':
            return monto_original / 2
        
        return 0
    
    def usar(self):
        """Incrementar el contador de usos"""
        if self.disponible:
            self.usos_realizados += 1
            self.save()

class VentaCombos(models.Model):
    """Para futura implementación de venta de combos"""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
