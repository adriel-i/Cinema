from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
import re
from datetime import datetime, timedelta

def validate_credit_card(number):
    """Validar número de tarjeta de crédito usando algoritmo de Luhn"""
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    
    # Remover espacios y guiones
    number = re.sub(r'[\s-]', '', number)
    
    # Verificar que solo contenga dígitos
    if not number.isdigit():
        raise ValidationError('El número de tarjeta solo debe contener dígitos.')
    
    # Verificar longitud (típicamente 13-19 dígitos)
    if len(number) < 13 or len(number) > 19:
        raise ValidationError('El número de tarjeta debe tener entre 13 y 19 dígitos.')
    
    # Verificar algoritmo de Luhn
    if luhn_checksum(number) != 0:
        raise ValidationError('El número de tarjeta no es válido.')

def validate_expiry_date(expiry_date):
    """Validar fecha de expiración de tarjeta"""
    try:
        # Formato esperado: MM/YY o MM/YYYY
        if '/' in expiry_date:
            parts = expiry_date.split('/')
            if len(parts) == 2:
                month = int(parts[0])
                year = int(parts[1])
                
                # Ajustar año si tiene 2 dígitos
                if year < 100:
                    current_year = datetime.now().year % 100
                    century = datetime.now().year // 100
                    if year < current_year:
                        century += 1
                    year += century * 100
                
                # Verificar mes
                if month < 1 or month > 12:
                    raise ValidationError('El mes de expiración no es válido.')
                
                # Verificar que no esté expirada
                expiry_datetime = datetime(year, month, 1)
                if expiry_datetime < datetime.now():
                    raise ValidationError('La tarjeta ha expirado.')
            else:
                raise ValidationError('Formato de fecha inválido. Use MM/YY o MM/YYYY.')
        else:
            raise ValidationError('Formato de fecha inválido. Use MM/YY o MM/YYYY.')
    except (ValueError, IndexError):
        raise ValidationError('Formato de fecha inválido. Use MM/YY o MM/YYYY.')

def validate_cvv(cvv):
    """Validar CVV/CVC"""
    if not cvv.isdigit():
        raise ValidationError('El CVV solo debe contener dígitos.')
    
    if len(cvv) not in [3, 4]:
        raise ValidationError('El CVV debe tener 3 o 4 dígitos.')

def validate_phone_number(phone):
    """Validar número de teléfono"""
    # Remover caracteres no numéricos excepto + y espacios
    cleaned = re.sub(r'[^\d+\s]', '', phone)
    
    # Verificar formato básico
    phone_pattern = r'^\+?[\d\s]{10,15}$'
    if not re.match(phone_pattern, cleaned):
        raise ValidationError('Formato de teléfono inválido.')

def validate_strong_password(password):
    """Validar contraseña fuerte"""
    errors = []
    
    if len(password) < 8:
        errors.append('La contraseña debe tener al menos 8 caracteres.')
    
    if not re.search(r'[A-Z]', password):
        errors.append('La contraseña debe contener al menos una mayúscula.')
    
    if not re.search(r'[a-z]', password):
        errors.append('La contraseña debe contener al menos una minúscula.')
    
    if not re.search(r'\d', password):
        errors.append('La contraseña debe contener al menos un número.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('La contraseña debe contener al menos un carácter especial.')
    
    # Verificar que no sea una contraseña común
    common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
    if password.lower() in common_passwords:
        errors.append('La contraseña es muy común. Elige una más segura.')
    
    if errors:
        raise ValidationError(errors)

def validate_dni(dni):
    """Validar DNI argentino"""
    # Remover caracteres no numéricos
    cleaned = re.sub(r'[^\d]', '', dni)
    
    if len(cleaned) not in [7, 8]:
        raise ValidationError('El DNI debe tener 7 u 8 dígitos.')
    
    # Verificar que no sea todo el mismo número
    if len(set(cleaned)) == 1:
        raise ValidationError('DNI inválido.')

def validate_future_date(date):
    """Validar que una fecha sea futura"""
    if date <= timezone.now().date():
        raise ValidationError('La fecha debe ser futura.')

def validate_business_hours(time):
    """Validar que una hora esté dentro del horario comercial (9:00 - 23:00)"""
    hour = time.hour
    if hour < 9 or hour >= 23:
        raise ValidationError('Las funciones deben estar entre las 9:00 y las 23:00.')

def validate_movie_duration(duration):
    """Validar duración de película (entre 60 y 300 minutos)"""
    if duration < 60 or duration > 300:
        raise ValidationError('La duración debe estar entre 60 y 300 minutos.')

def validate_seat_capacity(capacity):
    """Validar capacidad de sala (entre 20 y 500 asientos)"""
    if capacity < 20 or capacity > 500:
        raise ValidationError('La capacidad debe estar entre 20 y 500 asientos.')

def validate_price_range(price):
    """Validar rango de precios (entre $100 y $10000)"""
    if price < 100 or price > 10000:
        raise ValidationError('El precio debe estar entre $100 y $10,000.')

def validate_age(age):
    """Validar edad (entre 13 y 120 años)"""
    if age < 13 or age > 120:
        raise ValidationError('La edad debe estar entre 13 y 120 años.')

def validate_cupon_code(code):
    """Validar formato de código de cupón"""
    if not re.match(r'^[A-Z0-9]{4,10}$', code):
        raise ValidationError('El código debe tener 4-10 caracteres alfanuméricos en mayúsculas.')

def validate_session_key(session_key):
    """Validar clave de sesión"""
    if not session_key or len(session_key) < 32:
        raise ValidationError('Clave de sesión inválida.')

def validate_reservation_quantity(quantity):
    """Validar cantidad de entradas por reserva (máximo 10)"""
    if quantity < 1 or quantity > 10:
        raise ValidationError('Puedes reservar entre 1 y 10 entradas.')

def validate_image_size(file):
    """Validar tamaño de imagen (máximo 5MB)"""
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError('La imagen no puede ser mayor a 5MB.')

def validate_image_format(file):
    """Validar formato de imagen"""
    valid_formats = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in valid_formats:
        raise ValidationError('El formato debe ser JPEG, PNG o WebP.')

def validate_trailer_url(url):
    """Validar URL de trailer (YouTube o Vimeo)"""
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    vimeo_pattern = r'^(https?://)?(www\.)?vimeo\.com/[\d]+'
    
    if not re.match(youtube_pattern, url) and not re.match(vimeo_pattern, url):
        raise ValidationError('La URL debe ser de YouTube o Vimeo.')

class SecurityValidator:
    """Clase para validaciones de seguridad"""
    
    @staticmethod
    def validate_sql_injection(input_string):
        """Detectar posibles inyecciones SQL"""
        sql_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)',
            r'(--|\/\*|\*\/)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\bAND\b.*=.*\bAND\b)',
            r'(UNION.*SELECT)',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                raise ValidationError('Entrada no válida.')
    
    @staticmethod
    def validate_xss(input_string):
        """Detectar posibles ataques XSS"""
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'on\w+\s*=',
            r'javascript:',
            r'vbscript:',
            r'data:text/html',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                raise ValidationError('Entrada no válida.')
    
    @staticmethod
    def validate_csrf_token(token):
        """Validar token CSRF básico"""
        if not token or len(token) < 32:
            raise ValidationError('Token CSRF inválido.')
    
    @staticmethod
    def validate_api_key(api_key):
        """Validar formato de API key"""
        if not re.match(r'^[a-f0-9]{32,64}$', api_key):
            raise ValidationError('API key inválida.')

# Validadores personalizados para modelos Django
def validate_movie_title(title):
    """Validar título de película"""
    SecurityValidator.validate_sql_injection(title)
    SecurityValidator.validate_xss(title)
    
    if len(title.strip()) < 2:
        raise ValidationError('El título debe tener al menos 2 caracteres.')
    
    if len(title) > 200:
        raise ValidationError('El título no puede tener más de 200 caracteres.')

def validate_user_comment(comment):
    """Validar comentario de usuario"""
    SecurityValidator.validate_sql_injection(comment)
    SecurityValidator.validate_xss(comment)
    
    if len(comment.strip()) > 1000:
        raise ValidationError('El comentario no puede tener más de 1000 caracteres.')

def validate_search_query(query):
    """Validar consulta de búsqueda"""
    SecurityValidator.validate_sql_injection(query)
    SecurityValidator.validate_xss(query)
    
    if len(query.strip()) < 2:
        raise ValidationError('La búsqueda debe tener al menos 2 caracteres.')
    
    if len(query) > 100:
        raise ValidationError('La búsqueda no puede tener más de 100 caracteres.')
