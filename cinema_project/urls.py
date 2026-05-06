from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from reservas import views_qr

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('usuarios/', include('usuarios.urls')),
    path('peliculas/', include('peliculas.urls')),
    path('reservas/', include('reservas.urls')),
    # URLs para validación de QR
    path('validar-qr/<str:qr_hash>/', views_qr.validar_qr, name='validar_qr'),
    path('marcar-qr-usado/<str:qr_hash>/', views_qr.marcar_qr_usado, name='marcar_qr_usado'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
