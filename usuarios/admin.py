from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, PerfilUsuario

@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'rol', 'es_vip', 'puntos_fidelidad', 'is_staff')
    list_filter = ('rol', 'es_vip', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('rol', 'es_vip', 'puntos_fidelidad'),
            'description': 'Configuración de rol y privilegios del usuario'
        }),
        ('Información de Usuario', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'telefono', 'fecha_nacimiento')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'description': 'Permisos y acceso al sistema'
        }),
        ('Fidelidad', {
            'fields': ('es_vip', 'puntos_fidelidad'),
            'description': 'Programa de lealtad y beneficios VIP'
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined'),
            'description': 'Registro de actividad del usuario'
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'rol', 'password1', 'password2'),
            'description': 'Crear nuevo usuario. Selecciona el rol apropiado.'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Si es un usuario nuevo
            if form.cleaned_data.get('rol') == 'staff':
                obj.is_staff = True
            super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if obj and obj.rol == 'staff' and not request.user.is_superuser:
            readonly_fields.append('rol')
        return readonly_fields

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'notificaciones_email', 'notificaciones_sms', 'asientos_preferidos')
    search_fields = ('usuario__email', 'usuario__first_name', 'usuario__last_name')
    filter_horizontal = ('preferencias_genero',)
