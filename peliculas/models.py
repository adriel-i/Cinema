from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Genero(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name_plural = "Géneros"

class Pelicula(models.Model):
    ESTADOS_CHOICES = [
        ('prox_estreno', 'Próximo Estreno'),
        ('cartelera', 'En Cartelera'),
        ('finalizada', 'Finalizada'),
    ]
    
    CLASIFICACION_CHOICES = [
        ('ATP', 'Todo Público'),
        ('+13', '+13'),
        ('+16', '+16'),
        ('+18', '+18'),
    ]
    
    titulo = models.CharField(max_length=200)
    sinopsis = models.TextField()
    duracion = models.IntegerField(help_text="Duración en minutos")
    clasificacion = models.CharField(max_length=3, choices=CLASIFICACION_CHOICES)
    generos = models.ManyToManyField(Genero)
    director = models.CharField(max_length=100)
    actores_principales = models.TextField(help_text="Separar por comas")
    fecha_estreno = models.DateField()
    fecha_fin_cartelera = models.DateField(null=True, blank=True)
    poster = models.ImageField(upload_to='posters/')
    trailer_url = models.URLField(blank=True, help_text="URL del trailer de YouTube")
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='prox_estreno')
    idioma_original = models.CharField(max_length=50, default='Español')
    subtitulos = models.BooleanField(default=True)
    doblada = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.titulo
    
    @property
    def en_cartelera(self):
        return self.estado == 'cartelera' and self.fecha_estreno <= timezone.now().date() <= (self.fecha_fin_cartelera or timezone.now().date())
    
    @property
    def rating_promedio(self):
        ratings = self.rating_set.all()
        if ratings:
            return sum(r.puntuacion for r in ratings) / len(ratings)
        return 0

class Formato(models.Model):
    nombre = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    precio_adicional = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    def __str__(self):
        return self.nombre

class Rating(models.Model):
    pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['pelicula', 'usuario']
    
    def __str__(self):
        return f"{self.usuario} - {self.pelicula} - {self.puntuacion} estrellas"
