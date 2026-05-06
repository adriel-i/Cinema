from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
import uuid
import hashlib
import qrcode
import io
from django.core.files.base import ContentFile

class Funcion(models.Model):
    pelicula = models.ForeignKey('peliculas.Pelicula', on_delete=models.CASCADE)
    sala = models.ForeignKey('salas.Sala', on_delete=models.CASCADE)
    formato = models.ForeignKey('peliculas.Formato', on_delete=models.CASCADE)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    precio_base = models.DecimalField(max_digits=8, decimal_places=2)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.pelicula.titulo} - {self.fecha} {self.hora_inicio} - {self.sala.nombre}"
    
    @property
    def asientos_disponibles(self):
        """Contar asientos disponibles para esta función"""
        asientos_ocupados = Reserva.objects.filter(
            funcion=self,
            estado__in=['confirmada', 'temporal']
        ).values_list('asientos', flat=True)
        
        # Convertir lista de asientos a conjunto para comparación
        asientos_ocupados_set = set()
        for asientos_str in asientos_ocupados:
            asientos_ocupados_set.update(asientos_str.split(','))
        
        # Total de asientos de la sala menos los ocupados
        total_asientos = self.sala.capacidad_real
        return total_asientos - len(asientos_ocupados_set)
    
    @property
    def finalizada(self):
        """Verificar si la función ya finalizó"""
        datetime_fin = timezone.make_aware(
            timezone.datetime.combine(self.fecha, self.hora_fin)
        )
        return timezone.now() > datetime_fin

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('temporal', 'Temporal'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]
    
    codigo = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    funcion = models.ForeignKey(Funcion, on_delete=models.CASCADE)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    asientos = models.CharField(max_length=200)  # Almacenar como "A1,A2,A3"
    cantidad_entradas = models.IntegerField()
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='temporal')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Reserva {self.codigo} - {self.funcion}"
    
    def save(self, *args, **kwargs):
        if not self.fecha_expiracion:
            # Expirar después de 10 minutos si es temporal
            self.fecha_expiracion = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @property
    def expirada(self):
        """Verificar si la reserva temporal ha expirado"""
        return self.estado == 'temporal' and timezone.now() > self.fecha_expiracion
    
    @property
    def asientos_lista(self):
        """Retornar lista de asientos"""
        return self.asientos.split(',') if self.asientos else []
    
    def confirmar(self):
        """Confirmar la reserva"""
        if self.estado == 'temporal' and not self.expirada:
            self.estado = 'confirmada'
            self.fecha_confirmacion = timezone.now()
            self.save()
            return True
        return False
    
    def cancelar(self):
        """Cancelar la reserva"""
        if self.estado in ['temporal', 'confirmada']:
            self.estado = 'cancelada'
            self.save()
            return True
        return False
    
    def generar_qr(self):
        """Generar código QR para la reserva"""
        if not hasattr(self, 'validacion_qr'):
            # Crear hash único para el QR
            qr_data = f"{self.codigo}|{self.usuario.id}|{self.funcion.id}"
            qr_hash = hashlib.sha256(qr_data.encode()).hexdigest()
            
            # Crear ValidacionQR
            validacion = ValidacionQR.objects.create(
                reserva=self,
                qr_hash=qr_hash
            )
            
            # Generar imagen QR
            qr_url = f"http://127.0.0.1:8000/validar-qr/{qr_hash}/"
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Guardar imagen QR en el modelo
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return validacion
        return self.validacion_qr
    
    @property
    def qr_valido(self):
        """Verificar si el QR de la reserva es válido"""
        if hasattr(self, 'validacion_qr'):
            return self.validacion_qr.es_valido
        return False

class BloqueoAsiento(models.Model):
    """Modelo para manejar el bloqueo temporal de asientos"""
    funcion = models.ForeignKey(Funcion, on_delete=models.CASCADE)
    asiento = models.ForeignKey('salas.Asiento', on_delete=models.CASCADE)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    fecha_bloqueo = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()
    sesion_id = models.CharField(max_length=100)  # Para identificar la sesión del navegador
    
    def __str__(self):
        return f"Bloqueo {self.asiento.codigo} - {self.funcion}"
    
    @property
    def expirado(self):
        """Verificar si el bloqueo ha expirado"""
        return timezone.now() > self.fecha_expiracion
    
    @classmethod
    def bloquear_asiento(cls, funcion, asiento, usuario, sesion_id, minutos=10):
        """Bloquear un asiento temporalmente"""
        # Verificar si el asiento ya está bloqueado o reservado
        bloqueo_existente = cls.objects.filter(
            funcion=funcion,
            asiento=asiento,
            fecha_expiracion__gt=timezone.now()
        ).first()
        
        if bloqueo_existente:
            return False, "El asiento ya está bloqueado"
        
        # Verificar si el asiento está reservado
        reserva_existente = Reserva.objects.filter(
            funcion=funcion,
            asientos__contains=asiento.codigo,
            estado__in=['confirmada', 'temporal']
        ).first()
        
        if reserva_existente:
            return False, "El asiento ya está reservado"
        
        # Crear bloqueo
        cls.objects.create(
            funcion=funcion,
            asiento=asiento,
            usuario=usuario,
            sesion_id=sesion_id,
            fecha_expiracion=timezone.now() + timedelta(minutes=minutos)
        )
        
        return True, "Asiento bloqueado exitosamente"
    
    @classmethod
    def liberar_bloqueos_expirados(cls):
        """Liberar todos los bloqueos expirados"""
        cls.objects.filter(fecha_expiracion__lt=timezone.now()).delete()
    
    @classmethod
    def liberar_bloqueos_usuario(cls, usuario, sesion_id):
        """Liberar todos los bloqueos de un usuario en una sesión"""
        cls.objects.filter(usuario=usuario, sesion_id=sesion_id).delete()

class ValidacionQR(models.Model):
    """Modelo para registrar el uso de códigos QR"""
    reserva = models.OneToOneField('Reserva', on_delete=models.CASCADE, related_name='validacion_qr')
    qr_hash = models.CharField(max_length=64, unique=True)  # Hash único para validación
    usado = models.BooleanField(default=False)
    fecha_uso = models.DateTimeField(null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    ip_validacion = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Validación QR"
        verbose_name_plural = "Validaciones QR"
    
    def __str__(self):
        return f"QR {self.qr_hash[:8]}... - {self.reserva}"
    
    def marcar_como_usado(self, ip=None, user_agent=None):
        """Marcar el QR como usado"""
        self.usado = True
        self.fecha_uso = timezone.now()
        if ip:
            self.ip_validacion = ip
        if user_agent:
            self.user_agent = user_agent
        self.save()
    
    @property
    def es_valido(self):
        """Verificar si el QR es válido para uso"""
        return (
            not self.usado and 
            self.reserva.estado == 'confirmada' and
            not self.reserva.funcion.finalizada
        )

class TipoEntrada(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    precio_multiplicador = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
