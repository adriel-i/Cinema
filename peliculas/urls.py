from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    path('', views.cartelera, name='cartelera'),
    path('pelicula/<int:pelicula_id>/', views.detalle_pelicula, name='detalle'),
    path('buscar/', views.buscar_peliculas, name='buscar'),
    path('genero/<int:genero_id>/', views.peliculas_por_genero, name='por_genero'),
    path('calificar/<int:pelicula_id>/', views.calificar_pelicula, name='calificar'),
]
