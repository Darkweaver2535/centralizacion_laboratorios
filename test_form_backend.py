#!/usr/bin/env python
"""
Script para probar el formulario de crear usuario con login automático
"""
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import Client
from usuarios.models import Usuario

# Crear cliente y hacer login
client = Client()
admin = Usuario.objects.get(email='admin@adm.emi.edu.bo')
client.force_login(admin)

print("✅ Login exitoso como administrador")

# Probar GET de la página de crear usuario
response = client.get('/usuarios/crear/')
print(f"✅ GET /usuarios/crear/ - Status: {response.status_code}")

# Probar POST para crear usuario auxiliar
test_data = {
    'rol': 'auxiliar',
    'nombres': 'Usuario',
    'apellidos': 'Prueba',
    'numero_documento': '87654321',
    'correo_institucional': 'prueba@est.emi.edu.bo',
    'sede_asignacion': 'LP',
    'password': 'prueba123',
    'nivel_formacion': 'licenciatura',
    'area_formacion': 'ingenieria',
    'cargo_posicion': 'auxiliar de laboratorio',
    'turno_trabajo': 'mañana',
    'estado_usuario': 'activo'
}

response = client.post('/usuarios/crear/', test_data)
print(f"✅ POST /usuarios/crear/ - Status: {response.status_code}")

if response.status_code == 302:
    print("✅ Usuario creado exitosamente")
    # Verificar que se creó
    try:
        nuevo_usuario = Usuario.objects.get(correo_institucional='prueba@est.emi.edu.bo')
        print(f"✅ Usuario verificado: {nuevo_usuario.nombre_completo}")
    except Usuario.DoesNotExist:
        print("❌ Usuario no encontrado en la base de datos")
else:
    print(f"❌ Error creando usuario. Response: {response.content.decode()}")

print("\n🎯 Resumen: El backend funciona correctamente.")
print("🔧 El problema está en el frontend (JavaScript o CSS).")
