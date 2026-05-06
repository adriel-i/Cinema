from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TipoSala(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField()
    precio_multiplicador = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    
    def __str__(self):
        return self.nombre

class Sala(models.Model):
    nombre = models.CharField(max_length=50)
    tipo = models.ForeignKey(TipoSala, on_delete=models.PROTECT)
    capacidad_total = models.IntegerField()
    filas = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(26)])
    asientos_por_fila = models.IntegerField(validators=[MinValueValidator(1)])
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo.nombre})"
    
    @property
    def capacidad_real(self):
        """Capacidad real considerando asientos deshabilitados"""
        return self.asiento_set.filter(activo=True).count()
    
    def generar_asientos(self):
        """Generar automáticamente los asientos de la sala"""
        # Eliminar asientos existentes
        self.asiento_set.all().delete()
        
        for fila_num in range(1, self.filas + 1):
            fila_letra = chr(64 + fila_num)  # A, B, C, etc.
            for asiento_num in range(1, self.asientos_por_fila + 1):
                # Determinar tipo de asiento
                tipo_asiento = 'regular'
                if fila_num <= 2:  # Primeras filas
                    tipo_asiento = 'preferente'
                elif asiento_num in [1, self.asientos_por_fila]:  # Pasillos
                    tipo_asiento = 'pasillo'
                
                # Marcar algunos asientos como para discapacitados
                discapacitado = (fila_num == 1 and asiento_num in [1, 2])
                
                Asiento.objects.create(
                    sala=self,
                    fila=fila_letra,
                    numero=asiento_num,
                    tipo=tipo_asiento,
                    discapacitado=discapacitado
                )

class Asiento(models.Model):
    TIPO_CHOICES = [
        ('regular', 'Regular'),
        ('preferente', 'Preferente'),
        ('vip', 'VIP'),
        ('pasillo', 'Pasillo'),
    ]
    
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    fila = models.CharField(max_length=1)
    numero = models.IntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='regular')
    discapacitado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.sala.nombre} - {self.fila}{self.numero}"
    
    @property
    def codigo(self):
        return f"{self.fila}{self.numero}"
    
    class Meta:
        unique_together = ['sala', 'fila', 'numero']
        ordering = ['sala', 'fila', 'numero']
