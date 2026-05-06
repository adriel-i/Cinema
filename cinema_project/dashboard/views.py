from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate, TruncHour
import json

from peliculas.models import Pelicula
from reservas.models import Reserva, Funcion
from pagos.models import Pago
from usuarios.models import Usuario

def es_staff(user):
    return user.is_staff

@staff_member_required
def dashboard(request):
    """Dashboard principal con estadísticas"""
    hoy = timezone.now().date()
    semana_atras = hoy - timedelta(days=7)
    mes_atras = hoy - timedelta(days=30)
    
    # Estadísticas generales
    stats = {
        'peliculas_activas': Pelicula.objects.filter(activa=True).count(),
        'funciones_hoy': Funcion.objects.filter(fecha=hoy, activa=True).count(),
        'usuarios_totales': Usuario.objects.count(),
        'reservas_hoy': Reserva.objects.filter(fecha_creacion__date=hoy).count(),
    }
    
    # Ventas del último mes
    ventas_mes = Pago.objects.filter(
        fecha_creacion__gte=mes_atras,
        estado='completado'
    ).aggregate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    )
    
    # Ventas de hoy
    ventas_hoy = Pago.objects.filter(
        fecha_creacion__date=hoy,
        estado='completado'
    ).aggregate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    )
    
    # Películas más vendidas (último mes)
    peliculas_vendidas = Pelicula.objects.filter(
        funcion__reserva__pago__estado='completado',
        funcion__reserva__pago__fecha_creacion__gte=mes_atras
    ).annotate(
        ventas=Count('funcion__reserva__pago'),
        ingresos=Sum('funcion__reserva__pago__monto')
    ).order_by('-ventas')[:10]
    
    # Horarios más concurridos (última semana)
    horarios_concurridos = Funcion.objects.filter(
        reserva__pago__estado='completado',
        reserva__pago__fecha_creacion__gte=semana_atras
    ).annotate(
        asientos_vendidos=Count('reserva')
    ).order_by('-asientos_vendidos')[:10]
    
    # Ventas por día (última semana)
    ventas_diarias = Pago.objects.filter(
        fecha_creacion__gte=semana_atras,
        estado='completado'
    ).annotate(
        fecha=TruncDate('fecha_creacion')
    ).values('fecha').annotate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    ).order_by('fecha')
    
    # Ventas por hora (hoy)
    ventas_por_hora = Pago.objects.filter(
        fecha_creacion__date=hoy,
        estado='completado'
    ).annotate(
        hora=TruncHour('fecha_creacion')
    ).values('hora').annotate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    ).order_by('hora')
    
    # Ocupación de salas (hoy)
    ocupacion_salas = []
    for funcion in Funcion.objects.filter(fecha=hoy, activa=True):
        total_asientos = funcion.sala.capacidad_real
        asientos_vendidos = funcion.reserva_set.filter(
            estado='confirmada'
        ).aggregate(total=Sum('cantidad_entradas'))['total'] or 0
        
        ocupacion = (asientos_vendidos / total_asientos * 100) if total_asientos > 0 else 0
        
        ocupacion_salas.append({
            'funcion': funcion,
            'ocupacion': ocupacion,
            'vendidos': asientos_vendidos,
            'total': total_asientos
        })
    
    context = {
        'stats': stats,
        'ventas_mes': ventas_mes,
        'ventas_hoy': ventas_hoy,
        'peliculas_vendidas': peliculas_vendidas,
        'horarios_concurridos': horarios_concurridos,
        'ventas_diarias': json.dumps([
            {
                'fecha': v['fecha'].strftime('%Y-%m-%d'),
                'total': float(v['total'] or 0),
                'cantidad': v['cantidad']
            } for v in ventas_diarias
        ]),
        'ventas_por_hora': json.dumps([
            {
                'hora': v['hora'].strftime('%H:00'),
                'total': float(v['total'] or 0),
                'cantidad': v['cantidad']
            } for v in ventas_por_hora
        ]),
        'ocupacion_salas': ocupacion_salas,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
def reportes(request):
    """Página de reportes detallados"""
    return render(request, 'dashboard/reportes.html')

@staff_member_required
def reporte_ventas(request):
    """Reporte de ventas detallado"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    else:
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=30)
    
    pagos = Pago.objects.filter(
        fecha_creacion__date__gte=fecha_inicio,
        fecha_creacion__date__lte=fecha_fin,
        estado='completado'
    ).select_related('reserva__funcion__pelicula', 'metodo_pago', 'reserva__usuario')
    
    # Estadísticas
    total_ventas = pagos.aggregate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    )
    
    # Ventas por película
    ventas_por_pelicula = pagos.values(
        'reserva__funcion__pelicula__titulo'
    ).annotate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    ).order_by('-total')
    
    # Ventas por método de pago
    ventas_por_metodo = pagos.values(
        'metodo_pago__nombre'
    ).annotate(
        total=Sum('monto'),
        cantidad=Count('codigo')
    ).order_by('-total')
    
    context = {
        'pagos': pagos,
        'total_ventas': total_ventas,
        'ventas_por_pelicula': ventas_por_pelicula,
        'ventas_por_metodo': ventas_por_metodo,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'dashboard/reporte_ventas.html', context)

@staff_member_required
def reporte_ocupacion(request):
    """Reporte de ocupación de salas"""
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    else:
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=7)
    
    funciones = Funcion.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin,
        activa=True
    ).select_related('pelicula', 'sala', 'formato')
    
    datos_ocupacion = []
    for funcion in funciones:
        total_asientos = funcion.sala.capacidad_real
        asientos_vendidos = funcion.reserva_set.filter(
            estado='confirmada'
        ).aggregate(total=Sum('cantidad_entradas'))['total'] or 0
        
        ocupacion = (asientos_vendidos / total_asientos * 100) if total_asientos > 0 else 0
        ingresos = funcion.reserva_set.filter(
            estado='confirmada'
        ).aggregate(total=Sum('precio_total'))['total'] or 0
        
        datos_ocupacion.append({
            'funcion': funcion,
            'ocupacion': ocupacion,
            'vendidos': asientos_vendidos,
            'total': total_asientos,
            'ingresos': ingresos
        })
    
    context = {
        'datos_ocupacion': datos_ocupacion,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    
    return render(request, 'dashboard/reporte_ocupacion.html', context)

@staff_member_required
def reporte_clientes(request):
    """Reporte de clientes frecuentes"""
    clientes = Usuario.objects.annotate(
        total_compras=Count('reserva__pago', filter=Q(reserva__pago__estado='completado')),
        total_gastado=Sum('reserva__pago__monto', filter=Q(reserva__pago__estado='completado')),
        ultima_compra=Max('reserva__pago__fecha_creacion', filter=Q(reserva__pago__estado='completado'))
    ).filter(
        total_compras__gt=0
    ).order_by('-total_gastado')
    
    # Estadísticas de clientes
    stats_clientes = {
        'total_activos': clientes.count(),
        'vip': clientes.filter(es_vip=True).count(),
        'promedio_compras': clientes.aggregate(promedio=Avg('total_compras'))['promedio'] or 0,
        'promedio_gastado': clientes.aggregate(promedio=Avg('total_gastado'))['promedio'] or 0,
    }
    
    context = {
        'clientes': clientes,
        'stats_clientes': stats_clientes,
    }
    
    return render(request, 'dashboard/reporte_clientes.html', context)
