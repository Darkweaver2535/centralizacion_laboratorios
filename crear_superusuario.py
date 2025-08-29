#!/usr/bin/env python
"""
Script para crear el primer usuario administrador del sistema
Debe ejecutarse ANTES de aplicar las migraciones
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')

django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def crear_superusuario():
    """Crea el primer superusuario del sistema"""
    try:
        with transaction.atomic():
            # Verificar si ya existe un superusuario
            if User.objects.filter(is_superuser=True).exists():
                print("Ya existe un superusuario en el sistema.")
                return
            
            # Crear el usuario usando el manager personalizado
            admin_user = User.objects.create_superuser(
                correo_institucional='admin@emi.edu.bo',
                password='admin123',
                nombres='Administrador',
                apellidos='del Sistema',
                numero_documento='000000000',
                tipo_documento='ci'
            )
            
            print(f"Superusuario creado exitosamente:")
            print(f"Username: {admin_user.username}")
            print(f"Email: {admin_user.correo_institucional}")
            print(f"Password: admin123 (temporal)")
            print(f"Rol: {admin_user.get_rol_display()}")
            print(f"ID: {admin_user.id}")
            
    except Exception as e:
        print(f"Error al crear superusuario: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_superusuario()
