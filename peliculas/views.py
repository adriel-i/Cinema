from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Pelicula, Genero, Rating

def cartelera(request):
    """Vista principal con películas en cartelera"""
    hoy = timezone.now().date()
    
    # Películas en cartelera o activas
    peliculas_cartelera = Pelicula.objects.filter(
        Q(estado='cartelera') | Q(estado='prox_estreno'),
        activa=True
    ).order_by('fecha_estreno')
    
    # Próximos estrenos
    proximos_estrenos = Pelicula.objects.filter(
        estado='prox_estreno',
        activa=True,
        fecha_estreno__gt=hoy
    ).order_by('fecha_estreno')[:6]
    
    # Géneros para filtros
    generos = Genero.objects.all()
    
    # Filtros
    genero_id = request.GET.get('genero')
    if genero_id:
        peliculas_cartelera = peliculas_cartelera.filter(generos__id=genero_id)
    
    contexto = {
        'peliculas_cartelera': peliculas_cartelera,
        'proximos_estrenos': proximos_estrenos,
        'generos': generos,
        'genero_seleccionado': genero_id,
    }
    
    return render(request, 'peliculas/cartelera.html', contexto)

def detalle_pelicula(request, pelicula_id):
    """Detalle de una película específica"""
    pelicula = get_object_or_404(Pelicula, id=pelicula_id, activa=True)
    
    # Obtener funciones disponibles
    from reservas.models import Funcion
    hoy = timezone.now().date()
    funciones = Funcion.objects.filter(
        pelicula=pelicula,
        fecha__gte=hoy,
        activa=True
    ).order_by('fecha', 'hora_inicio')
    
    # Ratings de usuarios
    ratings = Rating.objects.filter(pelicula=pelicula).order_by('-fecha_creacion')[:10]
    usuario_ya_califico = False
    if request.user.is_authenticated:
        usuario_ya_califico = Rating.objects.filter(pelicula=pelicula, usuario=request.user).exists()
    
    contexto = {
        'pelicula': pelicula,
        'funciones': funciones,
        'ratings': ratings,
        'usuario_ya_califico': usuario_ya_califico,
    }
    
    return render(request, 'peliculas/detalle.html', contexto)

def buscar_peliculas(request):
    """Búsqueda de películas"""
    query = request.GET.get('q', '')
    peliculas = Pelicula.objects.filter(
        activa=True,
        titulo__icontains=query
    ).order_by('titulo')[:20]
    
    return render(request, 'peliculas/buscar.html', {
        'peliculas': peliculas,
        'query': query,
    })

def peliculas_por_genero(request, genero_id):
    """Películas filtradas por género"""
    genero = get_object_or_404(Genero, id=genero_id)
    peliculas = Pelicula.objects.filter(
        generos=genero,
        activa=True,
        estado='cartelera'
    ).order_by('titulo')
    
    return render(request, 'peliculas/genero.html', {
        'genero': genero,
        'peliculas': peliculas,
    })

@login_required
def calificar_pelicula(request, pelicula_id):
    """Calificar una película"""
    if request.method == 'POST':
        pelicula = get_object_or_404(Pelicula, id=pelicula_id)
        puntuacion = int(request.POST.get('puntuacion'))
        comentario = request.POST.get('comentario', '')
        
        # Verificar si ya calificó
        rating_existente = Rating.objects.filter(pelicula=pelicula, usuario=request.user).first()
        
        if rating_existente:
            rating_existente.puntuacion = puntuacion
            rating_existente.comentario = comentario
            rating_existente.save()
        else:
            Rating.objects.create(
                pelicula=pelicula,
                usuario=request.user,
                puntuacion=puntuacion,
                comentario=comentario
            )
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})
