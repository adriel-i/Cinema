from django.contrib import admin
from .models import Funcion, Reserva, BloqueoAsiento, TipoEntrada

@admin.register(TipoEntrada)
class TipoEntradaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_multiplicador', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(Funcion)
class FuncionAdmin(admin.ModelAdmin):
    list_display = ('pelicula', 'sala', 'fecha', 'hora_inicio', 'precio_base', 'activa')
    list_filter = ('fecha', 'activa', 'sala__tipo', 'formato')
    search_fields = ('pelicula__titulo', 'sala__nombre')
    date_hierarchy = 'fecha'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('pelicula', 'sala', 'formato')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'funcion', 'usuario', 'cantidad_entradas', 'precio_total', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'funcion__fecha')
    search_fields = ('codigo', 'usuario__email', 'funcion__pelicula__titulo')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_expiracion', 'fecha_confirmacion')
    
    fieldsets = (
        ('Información de reserva', {
            'fields': ('codigo', 'funcion', 'usuario', 'asientos', 'cantidad_entradas', 'precio_total')
        }),
        ('Estado y fechas', {
            'fields': ('estado', 'fecha_creacion', 'fecha_expiracion', 'fecha_confirmacion')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('funcion__pelicula', 'usuario')

@admin.register(BloqueoAsiento)
class BloqueoAsientoAdmin(admin.ModelAdmin):
    list_display = ('asiento', 'funcion', 'usuario', 'fecha_bloqueo', 'fecha_expiracion', 'sesion_id')
    list_filter = ('fecha_bloqueo', 'fecha_expiracion')
    search_fields = ('asiento__codigo', 'funcion__pelicula__titulo', 'usuario__email')
    date_hierarchy = 'fecha_bloqueo'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('asiento', 'funcion__pelicula', 'usuario')
