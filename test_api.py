#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import Client

# Crear cliente de prueba
client = Client()

# Probar la API exactamente como la llama el frontend
print("=== Probando API con categoria=equipos ===")
response = client.get('/visualizacion/api/buscar/?categoria=equipos')
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
print(f"Content: {response.content.decode()}")

print("\n=== Probando API con categoria=insumos ===")
response = client.get('/visualizacion/api/buscar/?categoria=insumos')
print(f"Status: {response.status_code}")
print(f"Content: {response.content.decode()}")

print("\n=== Probando API con categoria=guias ===")
response = client.get('/visualizacion/api/buscar/?categoria=guias')
print(f"Status: {response.status_code}")
print(f"Content: {response.content.decode()}")