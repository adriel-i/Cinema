from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from reservas.models import ValidacionQR
from .forms import StaffLoginForm

def staff_login(request):
    """Vista de login para personal del cine"""
    if request.user.is_authenticated and request.user.es_staff:
        return redirect('staff_dashboard')
    
    if request.method == 'POST':
        form = StaffLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            if user and user.es_staff:
                login(request, user)
                messages.success(request, f'Bienvenido {user.first_name}!')
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Credenciales inválidas o no tienes permisos de staff.')
    else:
        form = StaffLoginForm()
    
    return render(request, 'usuarios/staff_login.html', {'form': form})

@login_required
def staff_dashboard(request):
    """Dashboard principal para personal del cine"""
    if not request.user.es_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('staff_login')
    
    # Estadísticas del día
    hoy = timezone.now().date()
    validaciones_hoy = ValidacionQR.objects.filter(
        fecha_uso__date=hoy
    ).count()
    
    validaciones_totales = ValidacionQR.objects.count()
    
    # Validaciones recientes
    validaciones_recientes = ValidacionQR.objects.select_related('reserva', 'reserva__funcion__pelicula').order_by('-fecha_uso')[:10]
    
    context = {
        'validaciones_hoy': validaciones_hoy,
        'validaciones_totales': validaciones_totales,
        'validaciones_recientes': validaciones_recientes,
        'hoy': hoy,
    }
    
    return render(request, 'usuarios/staff_dashboard.html', context)

def staff_logout(request):
    """Logout para personal del cine"""
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('staff_login')
