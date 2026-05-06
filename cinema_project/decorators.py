from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
import time

def require_ajax(view_func):
    """Decorador para requerir que la petición sea AJAX"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden('Esta vista solo acepta peticiones AJAX')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def rate_limit(max_requests=10, window=60, key_func=lambda r: r.META.get('REMOTE_ADDR')):
    """Decorador para limitar la tasa de requests"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Usar cache para tracking de rate limit
            from django.core.cache import cache
            
            key = f'rate_limit:{key_func(request)}:{view_func.__name__}'
            count = cache.get(key, 0)
            
            if count >= max_requests:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Rate limit exceeded',
                        'message': f'Demasiadas solicitudes. Intenta de nuevo en {window} segundos.'
                    }, status=429)
                else:
                    messages.error(request, f'Demasiadas solicitudes. Intenta de nuevo en {window} segundos.')
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            
            # Incrementar contador
            cache.set(key, count + 1, window)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def validate_user_session(view_func):
    """Decorador para validar que la sesión del usuario sea válida"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Authentication required',
                    'message': 'Debes iniciar sesión para realizar esta acción.'
                }, status=401)
            else:
                messages.error(request, 'Debes iniciar sesión para realizar esta acción.')
                return redirect('usuarios:login')
        
        # Verificar última actividad
        last_activity = request.session.get('last_activity')
        if last_activity:
            from django.utils import timezone
            import datetime
            
            last_activity_time = datetime.datetime.fromisoformat(last_activity)
            session_timeout = 3600  # 1 hora
            
            if (timezone.now() - last_activity_time).total_seconds() > session_timeout:
                from django.contrib.auth import logout
                logout(request)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Session expired',
                        'message': 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
                    }, status=401)
                else:
                    messages.error(request, 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.')
                    return redirect('usuarios:login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def prevent_double_submit(view_func):
    """Decorador para prevenir doble envío de formularios"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'POST':
            # Generar token único para este formulario
            form_token = request.POST.get('form_token')
            session_token = request.session.get('form_token')
            
            if not form_token or form_token != session_token:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Invalid form token',
                        'message': 'El formulario no es válido o ya fue enviado.'
                    }, status=400)
                else:
                    messages.error(request, 'El formulario no es válido o ya fue enviado.')
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            
            # Limpiar token después de usarlo
            del request.session['form_token']
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def check_permissions(permission_name):
    """Decorador para verificar permisos específicos"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.has_perm(permission_name):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Permission denied',
                        'message': 'No tienes permisos para realizar esta acción.'
                    }, status=403)
                else:
                    messages.error(request, 'No tienes permisos para realizar esta acción.')
                    return redirect('index')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def validate_reservation_access(view_func):
    """Decorador para validar que el usuario pueda acceder a una reserva específica"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from reservas.models import Reserva
        
        reserva_id = kwargs.get('codigo') or kwargs.get('reserva_id')
        if not reserva_id:
            return HttpResponseForbidden('ID de reserva no proporcionado')
        
        try:
            reserva = Reserva.objects.get(codigo=reserva_id)
            
            # Verificar que la reserva pertenezca al usuario o que sea staff
            if reserva.usuario != request.user and not request.user.is_staff:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': 'Access denied',
                        'message': 'No puedes acceder a esta reserva.'
                    }, status=403)
                else:
                    messages.error(request, 'No puedes acceder a esta reserva.')
                    return redirect('index')
            
            # Agregar reserva al request para uso posterior
            request.reserva = reserva
            
        except Reserva.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Reservation not found',
                    'message': 'La reserva no existe.'
                }, status=404)
            else:
                messages.error(request, 'La reserva no existe.')
                return redirect('index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def log_user_activity(action_name):
    """Decorador para registrar actividades de usuario"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Ejecutar la vista
            response = view_func(request, *args, **kwargs)
            
            # Registrar actividad
            if request.user.is_authenticated:
                from django.utils import timezone
                from .models import UserActivity
                
                UserActivity.objects.create(
                    user=request.user,
                    action=action_name,
                    path=request.path,
                    method=request.method,
                    timestamp=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
            
            return response
        return _wrapped_view
    return decorator

# Decoradores combinados para uso común
ajax_login_required = require_ajax(login_required)
secure_post = require_POST(validate_user_session(prevent_double_submit))
staff_required = login_required(check_permissions('is_staff'))
