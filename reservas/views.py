from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST
from .models import Funcion, Reserva, BloqueoAsiento, TipoEntrada
from salas.models import Asiento
from peliculas.models import Pelicula
import json

def seleccionar_funcion(request, pelicula_id):
    """Seleccionar función para una película"""
    pelicula = get_object_or_404(Pelicula, id=pelicula_id, activa=True)
    hoy = timezone.now().date()
    
    # Obtener funciones disponibles
    funciones = Funcion.objects.filter(
        pelicula=pelicula,
        fecha__gte=hoy,
        activa=True
    ).order_by('fecha', 'hora_inicio')
    
    # Agrupar funciones por fecha
    funciones_por_fecha = {}
    for funcion in funciones:
        fecha_str = funcion.fecha.strftime('%Y-%m-%d')
        if fecha_str not in funciones_por_fecha:
            funciones_por_fecha[fecha_str] = []
        funciones_por_fecha[fecha_str].append(funcion)
    
    return render(request, 'reservas/seleccionar_funcion.html', {
        'pelicula': pelicula,
        'funciones_por_fecha': funciones_por_fecha,
    })

@login_required
def seleccionar_asientos(request, funcion_id):
    """Selección de asientos - CORAZÓN DEL SISTEMA"""
    funcion = get_object_or_404(Funcion, id=funcion_id, activa=True)
    
    # Limpiar bloqueos expirados
    BloqueoAsiento.liberar_bloqueos_expirados()
    
    # Obtener asientos de la sala
    asientos = funcion.sala.asiento_set.filter(activo=True).order_by('fila', 'numero')
    
    # Obtener asientos ocupados/bloqueados
    asientos_ocupados = set()
    asientos_bloqueados = set()
    
    # Asientos ya reservados
    reservas_confirmadas = Reserva.objects.filter(
        funcion=funcion,
        estado='confirmada'
    )
    for reserva in reservas_confirmadas:
        asientos_ocupados.update(reserva.asientos_lista)
    
    # Asientos bloqueados temporalmente
    bloqueos = BloqueoAsiento.objects.filter(
        funcion=funcion,
        fecha_expiracion__gt=timezone.now()
    )
    for bloqueo in bloqueos:
        asientos_bloqueados.add(bloqueo.asiento.codigo)
    
    # Liberar bloqueos del usuario actual en esta sesión
    if request.user.is_authenticated:
        sesion_id = request.session.session_key or 'anonymous'
        BloqueoAsiento.liberar_bloqueos_usuario(request.user, sesion_id)
    
    # Organizar asientos en matriz
    filas = {}
    for asiento in asientos:
        if asiento.fila not in filas:
            filas[asiento.fila] = []
        estado = 'disponible'
        if asiento.codigo in asientos_ocupados:
            estado = 'ocupado'
        elif asiento.codigo in asientos_bloqueados:
            estado = 'bloqueado'
        
        filas[asiento.fila].append({
            'asiento': asiento,
            'estado': estado,
            'codigo': asiento.codigo,
        })
    
    # Tipos de entrada disponibles con precios calculados
    tipos_entrada = []
    for tipo in TipoEntrada.objects.filter(activo=True):
        precio_calculado = funcion.precio_base * tipo.precio_multiplicador
        tipos_entrada.append({
            'tipo': tipo,
            'precio': precio_calculado
        })
    
    # Verificar tipos de asientos disponibles
    tiene_asientos_vip = funcion.sala.asiento_set.filter(tipo='vip').exists()
    tiene_asientos_discapacitados = funcion.sala.asiento_set.filter(discapacitado=True).exists()
    
    return render(request, 'reservas/seleccionar_asientos.html', {
        'funcion': funcion,
        'filas': filas,
        'tipos_entrada': tipos_entrada,
        'sesion_id': request.session.session_key or 'anonymous',
        'tiene_asientos_vip': tiene_asientos_vip,
        'tiene_asientos_discapacitados': tiene_asientos_discapacitados,
    })

@login_required
@require_POST
def bloquear_asiento(request):
    """Bloquear temporalmente un asiento"""
    try:
        data = json.loads(request.body)
        funcion_id = data.get('funcion_id')
        asiento_codigo = data.get('asiento_codigo')
        
        funcion = get_object_or_404(Funcion, id=funcion_id)
        asiento = get_object_or_404(funcion.sala.asiento_set, codigo=asiento_codigo)
        
        sesion_id = request.session.session_key or 'anonymous'
        
        # Intentar bloquear el asiento
        exito, mensaje = BloqueoAsiento.bloquear_asiento(
            funcion=funcion,
            asiento=asiento,
            usuario=request.user,
            sesion_id=sesion_id,
            minutos=10  # Bloqueo por 10 minutos
        )
        
        return JsonResponse({
            'success': exito,
            'message': mensaje,
            'asiento_codigo': asiento_codigo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@require_POST
def liberar_asiento(request):
    """Liberar un asiento bloqueado"""
    try:
        data = json.loads(request.body)
        funcion_id = data.get('funcion_id')
        asiento_codigo = data.get('asiento_codigo')
        
        funcion = get_object_or_404(Funcion, id=funcion_id)
        asiento = get_object_or_404(funcion.sala.asiento_set, codigo=asiento_codigo)
        sesion_id = request.session.session_key or 'anonymous'
        
        # Eliminar bloqueo
        BloqueoAsiento.objects.filter(
            funcion=funcion,
            asiento=asiento,
            usuario=request.user,
            sesion_id=sesion_id
        ).delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
@transaction.atomic
def crear_reserva(request, funcion_id):
    """Crear una reserva con los asientos seleccionados"""
    if request.method != 'POST':
        return redirect('reservas:seleccionar_asientos', funcion_id=funcion_id)
    
    try:
        funcion = get_object_or_404(Funcion, id=funcion_id)
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error al obtener la función: {str(e)}'
            })
        return redirect('reservas:seleccionar_asientos', funcion_id=funcion_id)
    
    # Manejar tanto peticiones AJAX como normales
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    try:
        # Liberar bloqueos de asientos del usuario actual ANTES de verificar disponibilidad
        sesion_id = request.session.session_key or 'anonymous'
        BloqueoAsiento.liberar_bloqueos_usuario(request.user, sesion_id)
        
        # Obtener asientos seleccionados
        asientos_param = request.POST.get('asientos', '')
        if asientos_param:
            asientos_seleccionados = asientos_param.split(',') if ',' in asientos_param else [asientos_param]
        else:
            asientos_seleccionados = request.POST.getlist('asientos')
        
        asientos_seleccionados = [a.strip() for a in asientos_seleccionados if a.strip()]
        
        if not asientos_seleccionados:
            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Por favor, selecciona al menos un asiento'
                })
            return redirect('reservas:seleccionar_asientos', funcion_id=funcion_id)
        
        # Verificar que los asientos estén disponibles
        asientos_ocupados = set()
        reservas_existentes = Reserva.objects.filter(
            funcion=funcion,
            estado__in=['confirmada', 'temporal']
        )
        
        print(f"DEBUG: Reservas existentes para función {funcion.id}:")
        for reserva in reservas_existentes:
            print(f"  - Reserva {reserva.codigo}: {reserva.asientos} (estado: {reserva.estado})")
            asientos_ocupados.update(reserva.asientos_lista)
        
        print(f"DEBUG: Asientos ocupados: {sorted(asientos_ocupados)}")
        print(f"DEBUG: Asientos seleccionados: {asientos_seleccionados}")
        
        # Verificar si algún asiento seleccionado está ocupado
        for asiento_codigo in asientos_seleccionados:
            if asiento_codigo in asientos_ocupados:
                print(f"DEBUG: Asiento {asiento_codigo} está ocupado")
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': f'El asiento {asiento_codigo} ya está ocupado'
                    })
                return redirect('reservas:seleccionar_asientos', funcion_id=funcion_id)
        
        # Calcular precio total
        precio_total = 0
        for asiento_codigo in asientos_seleccionados:
            try:
                # Extraer fila y número del código (ej: "A5" -> fila="A", numero=5)
                if len(asiento_codigo) >= 2:
                    fila = asiento_codigo[0]
                    numero = int(asiento_codigo[1:])
                else:
                    raise ValueError(f"Código de asiento inválido: {asiento_codigo}")
                
                asiento = funcion.sala.asiento_set.get(fila=fila, numero=numero)
                precio_base = funcion.precio_base
                
                # Aplicar multiplicadores de tipo de entrada
                tipo_entrada = request.POST.get('tipo_entrada', 'general')
                if tipo_entrada == 'vip':
                    precio_base *= 1.5
                elif tipo_entrada == 'preferente':
                    precio_base *= 1.2
                elif tipo_entrada == 'estudiante':
                    precio_base *= 0.8
                elif tipo_entrada == 'adulto mayor':
                    precio_base *= 0.9
                
                # Aplicar multiplicadores de tipo de asiento
                if asiento.tipo == 'vip':
                    precio_base *= 1.5
                elif asiento.tipo == 'preferente':
                    precio_base *= 1.2
                
                precio_total += precio_base
            except Asiento.DoesNotExist:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': f'El asiento {asiento_codigo} no existe'
                    })
                return redirect('reservas:seleccionar_asientos', funcion_id=funcion_id)
        
        # Crear reserva confirmada directamente (sin proceso de pago)
        reserva = Reserva.objects.create(
            funcion=funcion,
            usuario=request.user,
            asientos=','.join(asientos_seleccionados),
            cantidad_entradas=len(asientos_seleccionados),
            precio_total=precio_total,
            estado='confirmada'  # Confirmada directamente
        )
        
        # Generar QR para la reserva
        reserva.generar_qr()
        
        # Liberar bloqueos de asientos
        sesion_id = request.session.session_key or 'anonymous'
        BloqueoAsiento.liberar_bloqueos_usuario(request.user, sesion_id)
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': 'Reserva creada exitosamente',
                'reserva_id': str(reserva.codigo),  # Usar codigo en lugar de id
                'reserva_codigo': str(reserva.codigo),
                'redirect_url': '/usuarios/historial/'
            })
        
        return redirect('usuarios:historial_compras')
        
    except Exception as e:
        import traceback
        error_detalle = traceback.format_exc()
        print(f"ERROR EN crear_reserva: {str(e)}")
        print(f"TRACEBACK: {error_detalle}")
        
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear la reserva: {str(e)}'
            })
        return redirect('reservas:seleccionar_asientos', funcion_id=funcion_id)

@login_required
def estado_asientos(request, funcion_id):
    """API para obtener estado actual de los asientos"""
    funcion = get_object_or_404(Funcion, id=funcion_id)
    
    # Limpiar bloqueos expirados
    BloqueoAsiento.liberar_bloqueos_expirados()
    
    # Obtener estado de asientos
    asientos_ocupados = set()
    asientos_bloqueados = set()
    
    # Asientos reservados
    reservas = Reserva.objects.filter(
        funcion=funcion,
        estado__in=['confirmada', 'temporal']
    )
    for reserva in reservas:
        asientos_ocupados.update(reserva.asientos_lista)
    
    # Asientos bloqueados
    bloqueos = BloqueoAsiento.objects.filter(
        funcion=funcion,
        fecha_expiracion__gt=timezone.now()
    )
    for bloqueo in bloqueos:
        asientos_bloqueados.add(bloqueo.asiento.codigo)
    
    return JsonResponse({
        'ocupados': list(asientos_ocupados),
        'bloqueados': list(asientos_bloqueados),
        'disponibles': funcion.asientos_disponibles
    })
