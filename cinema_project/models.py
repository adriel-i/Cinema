from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class UserActivity(models.Model):
    """Modelo para registrar actividades de usuarios"""
    ACTION_CHOICES = [
        ('login', 'Inicio de sesión'),
        ('logout', 'Cierre de sesión'),
        ('register', 'Registro'),
        ('profile_update', 'Actualización de perfil'),
        ('reservation_create', 'Creación de reserva'),
        ('reservation_cancel', 'Cancelación de reserva'),
        ('payment_process', 'Procesamiento de pago'),
        ('movie_view', 'Visualización de película'),
        ('seat_select', 'Selección de asientos'),
        ('search', 'Búsqueda'),
        ('admin_access', 'Acceso administrativo'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"

class SecurityLog(models.Model):
    """Modelo para registrar eventos de seguridad"""
    EVENT_TYPES = [
        ('failed_login', 'Intento de login fallido'),
        ('blocked_ip', 'IP bloqueada'),
        ('suspicious_activity', 'Actividad sospechosa'),
        ('rate_limit_exceeded', 'Límite de tasa excedido'),
        ('invalid_api_key', 'API key inválida'),
        ('session_hijack_attempt', 'Intento de secuestro de sesión'),
        ('privilege_escalation', 'Escalada de privilegios'),
        ('data_breach_attempt', 'Intento de brecha de datos'),
    ]
    
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    severity = models.CharField(max_length=20, choices=[
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico')
    ])
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.severity} - {self.timestamp}"

class SystemConfiguration(models.Model):
    """Modelo para configuraciones del sistema"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key} = {self.value}"

class AuditLog(models.Model):
    """Modelo para auditoría de cambios en datos importantes"""
    ACTION_CHOICES = [
        ('create', 'Creación'),
        ('update', 'Actualización'),
        ('delete', 'Eliminación'),
        ('restore', 'Restauración'),
    ]
    
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    changes = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} {self.model_name} {self.object_id} - {self.timestamp}"
