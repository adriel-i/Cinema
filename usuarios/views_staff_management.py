from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Permission
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .models import Usuario
from .forms import CustomUserCreationForm

@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestion_staff(request):
    """Vista para gestionar usuarios staff desde el panel de administración"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Asignar rol de staff
            rol = request.POST.get('rol', 'cliente')
            if rol in ['staff', 'admin']:
                user.rol = rol
                if rol == 'staff':
                    user.is_staff = True
                elif rol == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                
                user.save()
                
                # Crear perfil de usuario automáticamente
                from .models import PerfilUsuario
                PerfilUsuario.objects.create(usuario=user)
                
                messages.success(request, f'Usuario {user.username} creado exitosamente como {rol}.')
                return redirect('admin:usuarios_usuario_change', user.pk)
            else:
                messages.error(request, 'Rol no válido para esta función.')
        else:
            form = CustomUserCreationForm()
    
    # Obtener usuarios existentes
    usuarios_staff = Usuario.objects.filter(rol__in=['staff', 'admin']).order_by('-date_joined')
    
    context = {
        'form': form,
        'usuarios_staff': usuarios_staff,
        'total_staff': usuarios_staff.count(),
        'total_admin': usuarios_staff.filter(rol='admin').count(),
        'total_personal': usuarios_staff.filter(rol='staff').count(),
    }
    
    return render(request, 'usuarios/gestion_staff.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_usuario_staff(request, user_id):
    """Editar usuario staff existente"""
    usuario = get_object_or_404(Usuario, pk=user_id)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Actualizar rol y permisos
            rol = request.POST.get('rol', usuario.rol)
            if rol in ['staff', 'admin']:
                usuario.is_staff = True
                if rol == 'admin':
                    usuario.is_superuser = True
                else:
                    usuario.is_superuser = False
            else:
                usuario.is_staff = False
                usuario.is_superuser = False
            
            usuario.save()
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            return redirect('admin:usuarios_usuario_change', usuario.pk)
    else:
        form = CustomUserCreationForm(instance=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/editar_usuario_staff.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_usuario_staff(request, user_id):
    """Eliminar usuario staff"""
    usuario = get_object_or_404(Usuario, pk=user_id)
    
    if request.method == 'POST':
        if request.POST.get('confirmar'):
            username = usuario.username
            usuario.delete()
            messages.success(request, f'Usuario {username} eliminado correctamente.')
            return redirect('admin:usuarios_usuario_changelist')
    
    context = {
        'usuario': usuario,
    }
    
    return render(request, 'usuarios/eliminar_usuario_staff.html', context)
