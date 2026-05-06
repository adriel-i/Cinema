from django.urls import path
from . import views
from . import views_qr

app_name = 'reservas'

urlpatterns = [
    path('pelicula/<int:pelicula_id>/', views.seleccionar_funcion, name='seleccionar_funcion'),
    path('funcion/<int:funcion_id>/asientos/', views.seleccionar_asientos, name='seleccionar_asientos'),
    path('funcion/<int:funcion_id>/reserva/', views.crear_reserva, name='crear_reserva'),
    path('funcion/<int:funcion_id>/estado/', views.estado_asientos, name='estado_asientos'),
    path('bloquear/', views.bloquear_asiento, name='bloquear_asiento'),
    path('liberar/', views.liberar_asiento, name='liberar_asiento'),
    # URLs para sistema de QR
    path('escaner/', views_qr.escaner_qr, name='escaner_qr'),
    path('regenerar-qr/<uuid:reserva_codigo>/', views_qr.regenerar_qr, name='regenerar_qr'),
]
