from django.contrib import admin
from .models import Pelicula, Genero, Formato, Rating

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Formato)
class FormatoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_adicional')
    search_fields = ('nombre',)

@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_estreno', 'clasificacion', 'estado', 'activa')
    list_filter = ('estado', 'clasificacion', 'generos', 'activa')
    search_fields = ('titulo', 'director', 'actores_principales')
    filter_horizontal = ('generos',)
    date_hierarchy = 'fecha_estreno'
    
    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'sinopsis', 'poster', 'trailer_url')
        }),
        ('Detalles técnicos', {
            'fields': ('duracion', 'clasificacion', 'idioma_original', 'subtitulos', 'doblada')
        }),
        ('Reparto', {
            'fields': ('director', 'actores_principales')
        }),
        ('Fechas y estado', {
            'fields': ('fecha_estreno', 'fecha_fin_cartelera', 'estado', 'activa')
        }),
        ('Géneros', {
            'fields': ('generos',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'usuario', 'puntuacion', 'fecha_creacion')
    list_filter = ('puntuacion', 'fecha_creacion')
    search_fields = ('pelicula__titulo', 'usuario__username', 'usuario__email')
    date_hierarchy = 'fecha_creacion'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pelicula', 'usuario')
