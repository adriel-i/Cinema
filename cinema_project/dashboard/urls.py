from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/ventas/', views.reporte_ventas, name='reporte_ventas'),
    path('reportes/ocupacion/', views.reporte_ocupacion, name='reporte_ocupacion'),
    path('reportes/clientes/', views.reporte_clientes, name='reporte_clientes'),
]
