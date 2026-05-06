from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
import time

class RateLimitMiddleware:
    """Middleware para limitar la tasa de requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = {}
    
    def __call__(self, request):
        # Obtener IP del cliente
        ip = self.get_client_ip(request)
        
        # Limitar requests por IP
        current_time = time.time()
        window_size = 60  # 1 minuto
        
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Limpiar requests antiguos
        self.requests[ip] = [req_time for req_time in self.requests[ip] 
                           if current_time - req_time < window_size]
        
        # Verificar límite
        max_requests = getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 100)
        if len(self.requests[ip]) >= max_requests:
            return JsonResponse({
                'error': 'Too many requests',
                'message': f'Limit of {max_requests} requests per minute exceeded'
            }, status=429)
        
        # Agregar request actual
        self.requests[ip].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class SecurityHeadersMiddleware:
    """Middleware para agregar headers de seguridad"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://code.jquery.com https://www.mercadopago.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.mercadopago.com; "
            "frame-src 'self' https://www.mercadopago.com; "
        )
        
        return response

class SessionSecurityMiddleware:
    """Middleware para seguridad de sesiones"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar sesión activa
        if request.user.is_authenticated:
            # Actualizar última actividad
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Verificar timeout de sesión
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
                session_timeout = getattr(settings, 'SESSION_TIMEOUT', 3600)  # 1 hora
                
                if (timezone.now() - last_activity_time).total_seconds() > session_timeout:
                    # Cerrar sesión por timeout
                    from django.contrib.auth import logout
                    logout(request)
                    return JsonResponse({
                        'error': 'Session expired',
                        'message': 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.'
                    }, status=401)
        
        response = self.get_response(request)
        return response

class APIKeyMiddleware:
    """Middleware para validar API keys en endpoints de API"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verificar si es un endpoint de API
        if request.path.startswith('/api/'):
            api_key = request.headers.get('X-API-Key')
            expected_key = getattr(settings, 'API_KEY', None)
            
            if expected_key and api_key != expected_key:
                return JsonResponse({
                    'error': 'Invalid API key',
                    'message': 'API key inválida o no proporcionada'
                }, status=401)
        
        response = self.get_response(request)
        return response
