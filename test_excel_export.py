#!/usr/bin/env python3
"""
Script de prueba para verificar que la funcionalidad de exportación Excel funciona correctamente
"""
import os
import sys
import django
import requests
from urllib.parse import urlencode

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

def test_excel_export():
    print("=" * 60)
    print("PRUEBA DE EXPORTACIÓN EXCEL")
    print("=" * 60)
    
    base_url = "http://localhost:8000/visualizacion/exportar-excel/"
    
    # Parámetros de prueba
    test_params = {
        'tipo': 'general',
        'unidad_academica': 'cochabamba',
        'semestre': '',
        'carrera': '',
        'materia': '',
        'laboratorio': '',
        'tipo_equipo': ''
    }
    
    tipos_exportacion = ['general', 'laboratorios', 'ensayos', 'equipos']
    
    print("\n1. Probando exportación para cada tipo:")
    print("-" * 40)
    
    for tipo in tipos_exportacion:
        test_params['tipo'] = tipo
        url = f"{base_url}?{urlencode(test_params)}"
        
        try:
            print(f"   Probando exportación: {tipo.upper()}")
            print(f"   URL: {url}")
            
            response = requests.get(url)
            
            if response.status_code == 200:
                print(f"   ✓ {tipo.upper()} - EXITOSO")
                print(f"     Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                print(f"     Content-Length: {len(response.content)} bytes")
                
                # Verificar que es un archivo Excel
                if response.headers.get('Content-Type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    print(f"     ✓ Formato Excel válido")
                else:
                    print(f"     ⚠ Formato Excel cuestionable")
                
            else:
                print(f"   ✗ {tipo.upper()} - ERROR {response.status_code}")
                print(f"     Error: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"   ✗ {tipo.upper()} - ERROR DE CONEXIÓN")
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
        url = f"{base_url}?{urlencode(filtro)}"
        
        try:
            print(f"   Probando filtro: {filtro}")
            response = requests.get(url)
            
            if response.status_code == 200:
                print(f"   ✓ EXITOSO - {len(response.content)} bytes")
            else:
                print(f"   ✗ ERROR {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ✗ ERROR DE CONEXIÓN: {str(e)}")
        
        print()
    
    print("=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == '__main__':
    test_excel_export()
