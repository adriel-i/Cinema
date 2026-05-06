from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, PerfilUsuario

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Apellido'}))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Teléfono'}))
    fecha_nacimiento = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}))
    dni = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'DNI'}))
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 'dni', 'telefono', 'fecha_nacimiento', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Nombre de Usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Confirmar Contraseña'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.telefono = self.cleaned_data['telefono']
        user.fecha_nacimiento = self.cleaned_data['fecha_nacimiento']
        if commit:
            user.save()
            # Crear perfil de usuario automáticamente
            PerfilUsuario.objects.create(usuario=user)
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario o Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'fecha_nacimiento')
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ('preferencias_genero', 'notificaciones_email', 'notificaciones_sms', 'asientos_preferidos')
        widgets = {
            'preferencias_genero': forms.CheckboxSelectMultiple(),
        }
