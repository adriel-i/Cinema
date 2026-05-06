from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    es_vip = models.BooleanField(default=False)
    puntos_fidelidad = models.IntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def agregar_puntos(self, puntos):
        """Agregar puntos de fidelidad"""
        self.puntos_fidelidad += puntos
        self.save()
    
    def canjear_puntos(self, puntos):
        """Canjear puntos de fidelidad"""
        if self.puntos_fidelidad >= puntos:
            self.puntos_fidelidad -= puntos
            self.save()
            return True
        return False

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    preferencias_genero = models.ManyToManyField('peliculas.Genero', blank=True)
    notificaciones_email = models.BooleanField(default=True)
    notificaciones_sms = models.BooleanField(default=False)
    asientos_preferidos = models.CharField(max_length=50, blank=True, 
                                          help_text="Ej: Centro, Pasillo, Preferente")
    
    def __str__(self):
        return f"Perfil de {self.usuario}"
