from django.contrib import admin
from .models import Sala, Asiento, TipoSala

@admin.register(TipoSala)
class TipoSalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_multiplicador', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'capacidad_total', 'filas', 'asientos_por_fila', 'activa')
    list_filter = ('tipo', 'activa')
    search_fields = ('nombre', 'tipo__nombre')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tipo')

@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'sala', 'tipo', 'discapacitado', 'activo')
    list_filter = ('tipo', 'discapacitado', 'activo', 'sala')
    search_fields = ('codigo', 'sala__nombre')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sala')
