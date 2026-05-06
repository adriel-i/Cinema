from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UsuarioUpdateForm, PerfilUsuarioForm
from .models import PerfilUsuario
from reservas.models import Reserva

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, '¡Cuenta creada exitosamente! Ya puedes iniciar sesión.')
            return redirect('usuarios:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.first_name}!')
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('index')

@login_required
def perfil(request):
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        user_form = UsuarioUpdateForm(request.POST, instance=request.user)
        perfil_form = PerfilUsuarioForm(request.POST, instance=perfil)
        
        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, '¡Perfil actualizado exitosamente!')
            return redirect('usuarios:perfil')
    else:
        user_form = UsuarioUpdateForm(instance=request.user)
        perfil_form = PerfilUsuarioForm(instance=perfil)
    
    context = {
        'user_form': user_form,
        'perfil_form': perfil_form
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def historial_compras(request):
    reservas = Reserva.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    
    # Calcular estadísticas
    total_gastado = sum(reserva.precio_total for reserva in reservas)
    confirmadas = reservas.filter(estado='confirmada').count()
    temporales = reservas.filter(estado='temporal').count()
    canceladas = reservas.filter(estado='cancelada').count()
    
    context = {
        'reservas': reservas,
        'total_gastado': total_gastado,
        'confirmadas': confirmadas,
        'temporales': temporales,
        'canceladas': canceladas,
    }
    return render(request, 'usuarios/historial.html', context)

@login_required
def detalle_reserva(request, codigo):
    from reservas.models import Reserva
    reserva = get_object_or_404(Reserva, codigo=codigo, usuario=request.user)
    
    # Generar QR si no existe
    if not hasattr(reserva, 'validacion_qr'):
        reserva.generar_qr()
        reserva.refresh_from_db()
    
    # Generar QR en base64 para mostrar en el template
    qr_base64 = None
    if hasattr(reserva, 'validacion_qr'):
        import qrcode
        import io
        import base64
        
        qr_url = f"http://127.0.0.1:8000/validar-qr/{reserva.validacion_qr.qr_hash}/"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'usuarios/detalle_reserva.html', {
        'reserva': reserva, 
        'qr_base64': qr_base64
    })

class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/password_reset_email.html'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    success_url = reverse_lazy('usuarios:password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'usuarios/password_reset_confirm.html'
    success_url = reverse_lazy('usuarios:password_reset_complete')
