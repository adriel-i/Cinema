from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'es_vip', 'puntos_fidelidad', 'is_staff')
    list_filter = ('es_vip', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fidelidad', {'fields': ('es_vip', 'puntos_fidelidad')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'notificaciones_email', 'notificaciones_sms', 'asientos_preferidos')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name')
    filter_horizontal = ('preferencias_genero',)
