#!/usr/bin/env python3
"""
Script de prueba para verificar que la funcionalidad de exportación Excel funciona correctamente
usando Django test client
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_excel_export_with_auth():
    print("=" * 60)
    print("PRUEBA DE EXPORTACIÓN EXCEL (CON AUTENTICACIÓN)")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba o usar uno existente
    try:
        user = User.objects.get(username='admin')
        print(f"Usando usuario existente: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        print(f"Creado usuario de prueba: {user.username}")
    
    # Hacer login
    login_success = client.login(username=user.username, password='testpass123' if user.username == 'testuser' else 'admin')
    if not login_success:
        print("ERROR: No se pudo hacer login")
        return
    
    print("✓ Login exitoso")
    
    tipos_exportacion = ['general', 'laboratorios', 'ensayos', 'equipos']
    
    print("\n1. Probando exportación para cada tipo:")
    print("-" * 40)
    
    for tipo in tipos_exportacion:
        print(f"   Probando exportación: {tipo.upper()}")
        
        try:
            response = client.get('/visualizacion/exportar-excel/', {
                'tipo': tipo,
                'unidad_academica': 'cochabamba',
                'semestre': '',
                'carrera': '',
                'materia': '',
                'laboratorio': '',
                'tipo_equipo': ''
            })
            
            if response.status_code == 200:
                print(f"   ✓ {tipo.upper()} - EXITOSO")
                print(f"     Content-Type: {response.get('Content-Type', 'N/A')}")
                print(f"     Content-Length: {len(response.content)} bytes")
                
                # Verificar que es un archivo Excel
                if response.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    print(f"     ✓ Formato Excel válido")
                    
                    # Verificar que hay contenido
                    if len(response.content) > 1000:
                        print(f"     ✓ Archivo tiene contenido apropiado")
                    else:
                        print(f"     ⚠ Archivo muy pequeño, posible problema")
                else:
                    print(f"     ⚠ Formato Excel cuestionable")
                    print(f"     Respuesta: {response.content[:200]}...")
                
            else:
                print(f"   ✗ {tipo.upper()} - ERROR {response.status_code}")
                print(f"     Respuesta: {response.content[:200]}...")
                
        except Exception as e:
            print(f"   ✗ {tipo.upper()} - EXCEPCIÓN")
            print(f"     Error: {str(e)}")
        
        print()
    
    print("\n2. Probando diferentes filtros:")
    print("-" * 40)
    
    filtros_prueba = [
        {'tipo': 'general', 'unidad_academica': 'la_paz'},
        {'tipo': 'laboratorios', 'semestre': '1'},
        {'tipo': 'ensayos', 'carrera': 'ingenieria_civil'},
        {'tipo': 'equipos', 'tipo_equipo': 'microscopio_optico'}
    ]
    
    for filtro in filtros_prueba:
        print(f"   Probando filtro: {filtro}")
        
        try:
            response = client.get('/visualizacion/exportar-excel/', filtro)
            
            if response.status_code == 200:
                print(f"   ✓ EXITOSO - {len(response.content)} bytes")
                if response.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    print(f"     ✓ Formato Excel válido")
            else:
                print(f"   ✗ ERROR {response.status_code}")
                print(f"     Respuesta: {response.content[:200]}...")
                
        except Exception as e:
            print(f"   ✗ EXCEPCIÓN: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == '__main__':
    test_excel_export_with_auth()
