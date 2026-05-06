from django.contrib import admin
from .models import Pago, MetodoPago, CuponDescuento, VentaCombos

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'reserva', 'metodo_pago', 'monto', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('codigo', 'reserva__codigo', 'transaccion_id')
    date_hierarchy = 'fecha_creacion'
    readonly_fields = ('codigo', 'fecha_creacion', 'respuesta_pago')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('reserva__funcion__pelicula', 'metodo_pago')

@admin.register(CuponDescuento)
class CuponDescuentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'tipo', 'valor', 'usos_realizados', 'usos_maximos', 'activo', 'fecha_fin')
    list_filter = ('tipo', 'activo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('codigo', 'descripcion')
    date_hierarchy = 'fecha_fin'
    filter_horizontal = ('peliculas_aplicables',)
    
    fieldsets = (
        ('Información básica', {
            'fields': ('codigo', 'tipo', 'valor', 'descripcion')
        }),
        ('Condiciones de uso', {
            'fields': ('uso_minimo_compra', 'usos_maximos', 'usos_realizados')
        }),
        ('Vigencia', {
            'fields': ('fecha_inicio', 'fecha_fin', 'activo')
        }),
        ('Aplicación', {
            'fields': ('peliculas_aplicables',)
        }),
    )

@admin.register(VentaCombos)
class VentaCombosAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre',)
