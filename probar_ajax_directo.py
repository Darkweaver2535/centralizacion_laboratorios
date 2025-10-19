#!/usr/bin/env python3

import requests
import json

def probar_ajax_directo():
    """Prueba AJAX directamente al servidor corriendo"""
    
    # URL del servidor local
    base_url = "http://127.0.0.1:8001"
    ajax_url = f"{base_url}/dashboard/ajax/asignaturas-por-carrera/"
    
    print("=== PRUEBA AJAX DIRECTA ===")
    
    # Probar con carrera que sabemos tiene problemas (carrera 23 - Ingeniería Industrial)
    params = {'carrera_id': 23}
    
    try:
        print(f"Llamando a: {ajax_url}")
        print(f"Parámetros: {params}")
        
        response = requests.get(ajax_url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            asignaturas = data.get('asignaturas', [])
            
            print(f"Asignaturas devueltas: {len(asignaturas)}")
            print("\nDetalle de cada asignatura:")
            
            for i, asig in enumerate(asignaturas, 1):
                nombre = asig.get('display') or asig.get('nombre', 'Sin nombre')
                print(f"  {i}. ID: {asig.get('id')} | Nombre: '{nombre}'")
                
                # Verificar los problemáticos
                if str(asig.get('id')) in ['168', '169', '171']:
                    print(f"    ⚠️  ID PROBLEMÁTICO: Este ID NO debería aparecer")
                elif nombre.strip() in ['168', '169', '171']:
                    print(f"    ⚠️  NOMBRE PROBLEMÁTICO: Este nombre NO debería aparecer")
                else:
                    print(f"    ✅ OK")
        else:
            print(f"Error: {response.status_code}")
            print(f"Contenido: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probar_ajax_directo()