#!/usr/bin/env python3
"""
Script para crear usuario de prueba para testing CKEditor
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from usuarios.models import Usuario

def crear_usuario_prueba():
    """Crear usuario de prueba si no existe"""
    
    username = 'test_ckeditor'
    email = 'test@ckeditor.com'
    password = 'test123'
    
    try:
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(username=username).exists():
            print(f"✅ Usuario '{username}' ya existe")
            user = Usuario.objects.get(username=username)
        else:
            # Crear nuevo usuario
            user = Usuario.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Test',
                last_name='CKEditor'
            )
            print(f"✅ Usuario '{username}' creado exitosamente")
        
        print(f"""
🔐 Credenciales de acceso:
   Usuario: {username}
   Email: {email}
   Contraseña: {password}
   
🌐 URL de acceso:
   http://127.0.0.1:8001/login/

📋 Para probar CKEditor:
   1. Hacer login con estas credenciales
   2. Ir a: http://127.0.0.1:8001/dashboard/malla-curricular/agregar-datos/
   3. Llenar campos básicos del formulario
   4. Hacer clic en "Agregar Grupo de Datos Adicionales"
   5. Los campos con CKEditor deberían aparecer automáticamente
        """)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

if __name__ == "__main__":
    crear_usuario_prueba()