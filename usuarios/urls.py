from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('historial/', views.historial_compras, name='historial'),
    path('reserva/<uuid:codigo>/', views.detalle_reserva, name='detalle_reserva'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
    
    # URLs para personal del cine
    path('staff/', views_staff.staff_login, name='staff_login'),
    path('staff/dashboard/', views_staff.staff_dashboard, name='staff_dashboard'),
    path('staff/logout/', views_staff.staff_logout, name='staff_logout'),
    
    # URLs para gestión de usuarios staff
    path('staff/gestion/', views_staff.gestion_staff, name='gestion_staff'),
    path('staff/editar/<int:user_id>/', views_staff.editar_usuario_staff, name='editar_usuario_staff'),
    path('staff/eliminar/<int:user_id>/', views_staff.eliminar_usuario_staff, name='eliminar_usuario_staff'),
]
