from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Intentar autenticar con username o email
            user = authenticate(request, username=username, password=password)
            
            # Si no funciona, intentar con el correo institucional
            if user is None and '@' in username:
                # Extraer username del correo
                username_from_email = username.split('@')[0]
                user = authenticate(request, username=username_from_email, password=password)
            
            if user is not None:
                login(request, user)
                # Redirigir según el rol
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Por favor corrija los errores del formulario')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

def registro_view(request):
    """Vista para registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.add_message(request, messages.SUCCESS, 'Registro exitoso. Ya puedes iniciar sesión.', extra_tags='success')
            return redirect('login:login')
        else:
            messages.error(request, 'Por favor corrija los errores del formulario')
    else:
        form = RegistroForm()
    
    return render(request, 'registro.html', {'form': form})

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('login:login')
