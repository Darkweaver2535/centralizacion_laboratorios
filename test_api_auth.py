#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

# Crear cliente de prueba
client = Client()

# Crear o obtener un usuario de prueba
User = get_user_model()
try:
    user = User.objects.get(username='admin')
    print(f"Usuario encontrado: {user.username}")
except User.DoesNotExist:
    print("Usuario admin no encontrado, creando uno temporal...")
    user = User.objects.create_user(username='test_user', password='test_password')

# Hacer login
client.force_login(user)

# Probar la API exactamente como la llama el frontend
print("=== Probando API con categoria=equipos (autenticado) ===")
response = client.get('/visualizacion/api/buscar/?categoria=equipos')
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
content = response.content.decode()
print(f"Content: {content[:500]}...")  # Primeros 500 caracteres

if response.status_code == 200:
    import json
    try:
        data = json.loads(content)
        print(f"Conteo de resultados: {data.get('count', 'N/A')}")
        print(f"Número de elementos: {len(data.get('results', []))}")
        if data.get('results'):
            print(f"Primer elemento: {data['results'][0]}")
    except json.JSONDecodeError:
        print("Error: Respuesta no es JSON válido")

print("\n=== Probando API con categoria=insumos (autenticado) ===")
response = client.get('/visualizacion/api/buscar/?categoria=insumos')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    try:
        data = json.loads(response.content.decode())
        print(f"Conteo de insumos: {data.get('count', 'N/A')}")
    except:
        print("Error procesando respuesta")

print("\n=== Probando API con categoria=guias (autenticado) ===")
response = client.get('/visualizacion/api/buscar/?categoria=guias')
print(f"Status: {response.status_code}")
if response.status_code == 200:
    try:
        data = json.loads(response.content.decode())
        print(f"Conteo de guías: {data.get('count', 'N/A')}")
    except:
        print("Error procesando respuesta")