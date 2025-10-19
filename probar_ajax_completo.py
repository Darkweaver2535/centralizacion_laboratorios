#!/usr/bin/env python3

import os
import sys
import django
import json
from django.test import Client
from django.urls import reverse

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, Asignatura

def probar_ajax_asignaturas():
    """Prueba exactamente lo que hace el AJAX del navegador"""
    print("=== PRUEBA COMPLETA DE AJAX ASIGNATURAS ===")
    
    # Crear cliente de prueba (simula navegador)
    client = Client()
    
    # Obtener todas las carreras disponibles
    carreras = Carrera.objects.all()
    print(f"Carreras disponibles: {carreras.count()}")
    
    for carrera in carreras:
        print(f"\n--- Probando carrera: {carrera.nombre} (ID: {carrera.id}) ---")
        
        # Llamar AJAX exactamente como lo hace el navegador
        try:
            response = client.get(
                reverse('core:asignaturas_por_carrera'),
                {'carrera_id': carrera.id}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                asignaturas = data.get('asignaturas', [])
                
                print(f"Asignaturas encontradas: {len(asignaturas)}")
                
                # Mostrar cada asignatura tal como la vería el navegador
                for i, asig in enumerate(asignaturas, 1):
                    nombre = asig.get('display') or asig.get('nombre', 'Sin nombre')
                    print(f"  {i}. ID: {asig.get('id')} | Nombre: '{nombre}'")
                    
                    # VERIFICAR SI APARECEN LOS PROBLEMÁTICOS
                    if str(asig.get('id')) in ['168', '169', '171']:
                        print(f"    ⚠️  PROBLEMÁTICO: Esta asignatura NO debería aparecer")
                    elif asig.get('id') in [168, 169, 171]:
                        print(f"    ⚠️  PROBLEMÁTICO: Esta asignatura NO debería aparecer")
                    elif nombre.strip() in ['168', '169', '171']:
                        print(f"    ⚠️  PROBLEMÁTICO: Nombre numérico NO debería aparecer")
                    else:
                        print(f"    ✅ OK: Asignatura válida")
                
                if not asignaturas:
                    print("  ➡️  Sin asignaturas (puede ser normal)")
                    
            else:
                print(f"ERROR: {response.status_code}")
                print(f"Contenido: {response.content.decode()}")
                
        except Exception as e:
            print(f"ERROR en AJAX: {e}")

    print("\n=== VERIFICACIÓN DIRECTA EN BASE DE DATOS ===")
    
    # Ver qué hay realmente en la base de datos
    asignaturas_problematicas = Asignatura.objects.filter(
        id__in=[168, 169, 171]
    )
    
    print(f"Asignaturas problemáticas en BD: {asignaturas_problematicas.count()}")
    for asig in asignaturas_problematicas:
        print(f"  ID {asig.id}: '{asig.nombre}' - Carrera: {asig.carrera}")
    
    # Ver asignaturas con nombres numéricos
    asignaturas_numericas = Asignatura.objects.filter(
        nombre__regex=r'^\d+$'
    )
    
    print(f"\nAsignaturas con nombres puramente numéricos: {asignaturas_numericas.count()}")
    for asig in asignaturas_numericas:
        print(f"  ID {asig.id}: '{asig.nombre}' - Carrera: {asig.carrera}")

if __name__ == "__main__":
    probar_ajax_asignaturas()