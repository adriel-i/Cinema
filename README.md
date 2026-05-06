# CineMax - Sistema de Gestión de Cines

Un sistema web completo para la gestión de cines con todas las funcionalidades modernas necesarias para una experiencia cinematográfica excepcional.

## 🎬 Características Principales

### Módulo de Clientes (Frontend)
- ✅ Registro e inicio de sesión de usuarios
- ✅ Recuperación de contraseña
- ✅ Perfil de usuario con preferencias
- ✅ Historial de compras
- ✅ Programa de puntos y fidelidad
- ✅ Cartelera de películas con filtros
- ✅ Detalle completo de películas (trailer, sinopsis, rating)
- ✅ **Sistema avanzado de selección de asientos**
- ✅ Compra de entradas con múltiples métodos de pago
- ✅ Cupones de descuento y promociones
- ✅ Tickets digitales con código QR

### Módulo Administrativo (Backend)
- ✅ Gestión completa de películas
- ✅ Gestión de salas y asientos
- ✅ Creación y programación de funciones
- ✅ Panel administrativo con dashboard
- ✅ Reportes detallados de ventas y ocupación
- ✅ Gestión de usuarios y reservas
- ✅ Sistema de promociones y descuentos
- ✅ Análisis estadístico en tiempo real

### Características Técnicas Destacadas
- 🔥 **Lógica de bloqueo de asientos en tiempo real** (corazón del sistema)
- 🛡️ Sistema de seguridad avanzado
- 📊 Dashboard con estadísticas y gráficos
- 💳 Integración con Mercado Pago
- 📱 Diseño responsive con Bootstrap 5
- 🔄 Sistema de notificaciones
- 🎫 Generación de tickets digitales

## 🏗️ Arquitectura y Tecnologías

### Backend
- **Framework**: Django 4.2.7
- **Base de datos**: PostgreSQL
- **Cache**: Redis
- **Pagos**: Mercado Pago API
- **Tareas asíncronas**: Celery

### Frontend
- **Framework**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Iconos**: Font Awesome 6
- **Gráficos**: Chart.js (para dashboard)

### Seguridad
- 🔒 Protección contra inyección SQL, XSS, CSRF
- 🚦 Rate limiting por IP
- 🛡️ Headers de seguridad
- 👤 Auditoría de actividades
- 🔐 Validaciones de datos robustas

## 📋 Requisitos del Sistema

### Software
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js (para herramientas de desarrollo)

### Hardware
- Mínimo 2GB RAM
- 10GB espacio en disco
- Procesador de 2 núcleos

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <repositorio-url>
cd CINEMA
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copiar `.env.example` a `.env` y configurar:
```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:
```env
SECRET_KEY=tu-secret-key-aqui
DEBUG=True
DB_NAME=cinema_db
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

# Mercado Pago
MERCADO_PAGO_ACCESS_TOKEN=tu-access-token
MERCADO_PAGO_PUBLIC_KEY=tu-public-key

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 5. Configurar base de datos
```bash
# Crear base de datos PostgreSQL
createdb cinema_db

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario
```bash
python manage.py createsuperuser
```

### 7. Recolectar archivos estáticos
```bash
python manage.py collectstatic
```

### 8. Iniciar servidor de desarrollo
```bash
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
CINEMA/
├── cinema_project/          # Configuración principal
│   ├── settings.py         # Configuración de Django
│   ├── urls.py            # URLs principales
│   ├── middleware.py      # Middleware personalizado
│   ├── decorators.py      # Decoradores de seguridad
│   ├── validators.py      # Validaciones personalizadas
│   └── dashboard/         # Vistas de dashboard
├── usuarios/               # Módulo de usuarios
├── peliculas/              # Módulo de películas
├── salas/                 # Módulo de salas
├── reservas/              # Módulo de reservas (CORAZÓN)
├── pagos/                 # Módulo de pagos
├── templates/             # Plantillas HTML
├── static/                # Archivos estáticos
├── media/                 # Archivos multimedia
├── requirements.txt       # Dependencias Python
└── manage.py             # Script de gestión Django
```

## 🎯 Funcionalidades Clave

### Sistema de Bloqueo de Asientos (El Corazón del Sistema)

El sistema implementa un mecanismo sofisticado de bloqueo temporal de asientos:

1. **Bloqueo en tiempo real**: Cuando un usuario selecciona un asiento, se bloquea por 10 minutos
2. **Liberación automática**: Los bloqueos expiran automáticamente
3. **Prevención de doble reserva**: No permite reservar asientos ya bloqueados
4. **Gestión por sesión**: Cada usuario tiene sus propios bloqueos
5. **API RESTful**: Endpoints para consulta y gestión de estado

### Métodos de Pago Integrados

- **Mercado Pago**: Integración completa con webhooks
- **Transferencia bancaria**: Instrucciones automáticas
- **Pago simulado**: Para testing y desarrollo

### Dashboard Administrativo

Panel completo con:
- 📊 Ventas por día/período
- 🎬 Películas más vendidas
- 🕐 Horarios más concurridos
- 👥 Estadísticas de clientes
- 💰 Ingresos y ocupación

## 🔧 Configuración Adicional

### Configuración de Mercado Pago

1. Crear cuenta en [Mercado Pago Developers](https://www.mercadopago.com/developers)
2. Obtener credenciales (ACCESS_TOKEN y PUBLIC_KEY)
3. Configurar webhooks en el panel de Mercado Pago
4. Actualizar variables de entorno

### Configuración de Redis

```bash
# Instalar Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Iniciar Redis
redis-server
```

### Configuración de PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres createuser --interactive
sudo -u postgres createdb cinema_db
sudo -u postgres psql cinema_db
GRANT ALL PRIVILEGES ON DATABASE cinema_db TO tu_usuario;
```

## 🧪 Testing

### Ejecutar tests
```bash
python manage.py test
```

### Tests específicos
```bash
python manage.py test usuarios
python manage.py test reservas
python manage.py test pagos
```

## 📊 Monitoreo y Logs

El sistema incluye logging completo:
- **Logs de aplicación**: `/logs/cinema.log`
- **Logs de seguridad**: `/logs/security.log`
- **Auditoría de usuarios**: Base de datos `UserActivity`

## 🔒 Seguridad Implementada

### Middleware de Seguridad
- Rate limiting por IP
- Headers de seguridad (CSP, HSTS, XSS Protection)
- Validación de sesión
- Protección CSRF

### Validaciones
- Inyección SQL
- Cross-site Scripting (XSS)
- Cross-site Request Forgery (CSRF)
- Validación de datos de entrada

### Auditoría
- Registro de actividades de usuarios
- Logs de eventos de seguridad
- Trazabilidad de cambios importantes

## 🚀 Despliegue en Producción

### Configuración de Producción

1. **Variables de entorno**:
```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
SECRET_KEY=tu-secret-key-produccion
```

2. **Base de datos PostgreSQL** production-ready
3. **Servidor web**: Nginx + Gunicorn
4. **SSL**: Certificado SSL/TLS
5. **Backup**: Sistema de backup automático

### Comandos de Despliegue
```bash
# Recolectar estáticos
python manage.py collectstatic --noinput

# Migraciones
python manage.py migrate

# Crear superusuario si no existe
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password')" 2>/dev/null || echo "Admin user exists"
```

## 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit de cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. Push al branch: `git push origin feature/nueva-funcionalidad`
5. Pull Request

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para detalles.

## 🆘 Soporte

Para soporte técnico:
- 📧 Email: soporte@cinemax.com
- 📞 Teléfono: +54 9 11 1234-5678
- 💬 Chat: Disponible en el sitio web

## 🔄 Versiones

- **v1.0.0**: Versión inicial con funcionalidades básicas
- **v1.1.0**: Agregado sistema de promociones
- **v1.2.0**: Mejoras en seguridad y rendimiento
- **v2.0.0**: Versión actual con todas las funcionalidades

---

**CineMax** - Tu experiencia cinematográfica, simplificada. 🎬✨
