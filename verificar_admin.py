#!/usr/bin/env python
"""
Script para verificar datos del usuario administrador
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')

django.setup()

from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

print("=== VERIFICACIÓN DEL USUARIO ADMINISTRADOR ===")

try:
    admin = User.objects.get(id=1)
    print(f"✅ Usuario encontrado:")
    print(f"   ID: {admin.id}")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Correo institucional: {admin.correo_institucional}")
    print(f"   Es activo: {admin.is_active}")
    print(f"   Es superuser: {admin.is_superuser}")
    print(f"   Fecha registro: {admin.date_joined}")
    
    print(f"\n=== CONFIGURACIÓN DEL MODELO ===")
    print(f"   USERNAME_FIELD: {User.USERNAME_FIELD}")
    print(f"   EMAIL_FIELD: {User.EMAIL_FIELD}")
    print(f"   REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")
    
    print(f"\n=== PRUEBAS DE AUTENTICACIÓN ===")
    
    # Probar autenticación con diferentes combinaciones
    test_cases = [
        ('admin', 'admin123'),
        ('admin@emi.edu.bo', 'admin123'),
        (admin.username, 'admin123'),
        (admin.correo_institucional, 'admin123'),
        (admin.email, 'admin123'),
    ]
    
    for username, password in test_cases:
        user = authenticate(username=username, password=password)
        status = "✅ ÉXITO" if user else "❌ FALLO"
        print(f"   {status}: '{username}' + '{password}'")
        
    print(f"\n=== PRUEBA CON BACKEND PERSONALIZADO ===")
    from usuarios.backends import FlexibleAuthBackend
    backend = FlexibleAuthBackend()
    
    for username, password in test_cases:
        user = backend.authenticate(None, username=username, password=password)
        status = "✅ ÉXITO" if user else "❌ FALLO"
        print(f"   {status}: '{username}' + '{password}' (Backend personalizado)")
        
except User.DoesNotExist:
    print("❌ No se encontró el usuario administrador")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
