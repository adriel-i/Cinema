from django.urls import path
from . import views

app_name = 'salas'

urlpatterns = [
    path('', views.lista_salas, name='lista'),
    path('<int:sala_id>/', views.detalle_sala, name='detalle'),
    path('<int:sala_id>/generar-asientos/', views.generar_asientos_sala, name='generar_asientos'),
    path('funcion/<int:funcion_id>/estado/', views.estado_sala_funcion, name='estado_funcion'),
]
