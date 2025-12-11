from django import forms
from django.contrib.auth.forms import UserCreationForm
from usuarios.models import Usuario
from django.core.exceptions import ValidationError

class RegistroForm(forms.ModelForm):
    """Formulario de registro para nuevos usuarios"""
    
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        }),
        help_text='Mínimo 8 caracteres'
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su contraseña'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['nombres', 'apellidos', 'numero_documento', 'correo_institucional', 
                  'telefono_personal', 'sede_asignacion']
        widgets = {
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese sus nombres'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese sus apellidos'
            }),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de CI'
            }),
            'correo_institucional': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@emi.edu.bo'
            }),
            'telefono_personal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(Opcional)'
            }),
            'sede_asignacion': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'numero_documento': 'Carnet de Identidad',
            'correo_institucional': 'Correo Institucional',
            'telefono_personal': 'Teléfono Personal',
            'sede_asignacion': 'Sede',
        }
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Las contraseñas no coinciden')
        
        if password1 and len(password1) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        return password2
    
    def clean_correo_institucional(self):
        correo = self.cleaned_data.get('correo_institucional')
        if Usuario.objects.filter(correo_institucional=correo).exists():
            raise ValidationError('Este correo institucional ya está registrado')
        return correo
    
    def clean_numero_documento(self):
        numero = self.cleaned_data.get('numero_documento')
        if Usuario.objects.filter(numero_documento=numero).exists():
            raise ValidationError('Este número de documento ya está registrado')
        return numero
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.username = self.cleaned_data['correo_institucional'].split('@')[0]
        user.email = self.cleaned_data['correo_institucional']
        user.estado_usuario = 'activo'
        user.debe_cambiar_password = False
        user.rol = 'docente'  # Rol por defecto
        
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Formulario de login"""
    username = forms.CharField(
        label='Usuario o Correo Institucional',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'admin o admin@emi.edu.bo'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña'
        })
    )
