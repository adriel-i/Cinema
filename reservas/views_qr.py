from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import ValidacionQR
import json

def validar_qr(request, qr_hash):
    """Vista para validar un código QR"""
    try:
        validacion = get_object_or_404(ValidacionQR, qr_hash=qr_hash)
        reserva = validacion.reserva
        
        context = {
            'validacion': validacion,
            'reserva': reserva,
            'es_valido': validacion.es_valido,
            'ya_usado': validacion.usado,
        }
        
        return render(request, 'reservas/validar_qr.html', context)
        
    except Exception as e:
        return render(request, 'reservas/qr_invalido.html', {
            'error': str(e)
        })

@csrf_exempt
def marcar_qr_usado(request, qr_hash):
    """Vista AJAX para marcar un QR como usado"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        validacion = get_object_or_404(ValidacionQR, qr_hash=qr_hash)
        
        if validacion.usado:
            return JsonResponse({
                'success': False, 
                'message': 'Este código QR ya ha sido utilizado'
            })
        
        if not validacion.es_valido:
            return JsonResponse({
                'success': False, 
                'message': 'Este código QR no es válido'
            })
        
        # Marcar como usado
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        validacion.marcar_como_usado(ip=ip, user_agent=user_agent)
        
        return JsonResponse({
            'success': True,
            'message': 'Código QR validado exitosamente',
            'reserva': {
                'codigo': str(validacion.reserva.codigo),
                'pelicula': validacion.reserva.funcion.pelicula.titulo,
                'asientos': validacion.reserva.asientos_lista,
                'fecha': validacion.reserva.funcion.fecha.strftime('%d/%m/%Y'),
                'hora': validacion.reserva.funcion.hora_inicio.strftime('%H:%M')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al validar el código QR: {str(e)}'
        })

def escaner_qr(request):
    """Vista principal del escáner de QR"""
    return render(request, 'reservas/escaner_qr.html')

@csrf_exempt
def regenerar_qr(request, reserva_codigo):
    """Vista para regenerar el QR de una reserva"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'})
    
    try:
        from .models import Reserva
        reserva = get_object_or_404(Reserva, codigo=reserva_codigo)
        
        # Eliminar QR existente si hay uno
        if hasattr(reserva, 'validacion_qr'):
            reserva.validacion_qr.delete()
        
        # Generar nuevo QR
        nueva_validacion = reserva.generar_qr()
        
        return JsonResponse({
            'success': True,
            'message': 'QR regenerado exitosamente',
            'qr_hash': nueva_validacion.qr_hash
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al regenerar QR: {str(e)}'
        })
