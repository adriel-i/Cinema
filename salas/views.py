from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count
from .models import Sala, Asiento, TipoSala

def es_staff(user):
    return user.is_staff

@staff_member_required
def lista_salas(request):
    """Listar todas las salas (solo staff)"""
    salas = Sala.objects.select_related('tipo').annotate(
        asientos_count=Count('asiento', filter=models.Q(asiento__activo=True))
    ).order_by('nombre')
    
    return render(request, 'salas/lista_salas.html', {'salas': salas})

@staff_member_required
def detalle_sala(request, sala_id):
    """Ver detalles de una sala (solo staff)"""
    sala = get_object_or_404(Sala, id=sala_id)
    asientos = sala.asiento_set.filter(activo=True).order_by('fila', 'numero')
    
    # Organizar asientos en matriz
    filas = {}
    for asiento in asientos:
        if asiento.fila not in filas:
            filas[asiento.fila] = []
        filas[asiento.fila].append(asiento)
    
    return render(request, 'salas/detalle_sala.html', {
        'sala': sala,
        'filas': filas,
    })

@staff_member_required
def generar_asientos_sala(request, sala_id):
    """Generar automáticamente los asientos de una sala"""
    sala = get_object_or_404(Sala, id=sala_id)
    
    if request.method == 'POST':
        sala.generar_asientos()
        return JsonResponse({'success': True, 'message': f'Asientos generados para {sala.nombre}'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})

def estado_sala_funcion(request, funcion_id):
    """API para obtener estado de asientos de una sala para una función"""
    from reservas.models import Funcion, Reserva, BloqueoAsiento
    
    funcion = get_object_or_404(Funcion, id=funcion_id)
    
    # Obtener todos los asientos de la sala
    asientos = funcion.sala.asiento_set.filter(activo=True).order_by('fila', 'numero')
    
    # Obtener asientos ocupados
    asientos_ocupados = set()
    reservas = Reserva.objects.filter(
        funcion=funcion,
        estado='confirmada'
    )
    for reserva in reservas:
        asientos_ocupados.update(reserva.asientos_lista)
    
    # Obtener asientos bloqueados
    asientos_bloqueados = set()
    bloqueos = BloqueoAsiento.objects.filter(
        funcion=funcion,
        fecha_expiracion__gt=timezone.now()
    )
    for bloqueo in bloqueos:
        asientos_bloqueados.add(bloqueo.asiento.codigo)
    
    # Construir respuesta
    asientos_info = []
    for asiento in asientos:
        estado = 'disponible'
        if asiento.codigo in asientos_ocupados:
            estado = 'ocupado'
        elif asiento.codigo in asientos_bloqueados:
            estado = 'bloqueado'
        
        asientos_info.append({
            'codigo': asiento.codigo,
            'fila': asiento.fila,
            'numero': asiento.numero,
            'tipo': asiento.tipo,
            'discapacitado': asiento.discapacitado,
            'estado': estado
        })
    
    return JsonResponse({
        'sala': {
            'nombre': funcion.sala.nombre,
            'tipo': funcion.sala.tipo.nombre,
            'capacidad': funcion.sala.capacidad_real
        },
        'asientos': asientos_info,
        'totales': {
            'disponibles': len([a for a in asientos_info if a['estado'] == 'disponible']),
            'ocupados': len([a for a in asientos_info if a['estado'] == 'ocupado']),
            'bloqueados': len([a for a in asientos_info if a['estado'] == 'bloqueado'])
        }
    })
