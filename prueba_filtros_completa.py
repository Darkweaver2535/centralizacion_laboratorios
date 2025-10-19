#!/usr/bin/env python3

import os
import django
import requests
import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera, UnidadAcademica

def probar_filtros_completos():
    """Prueba completa de todos los filtros en la interfaz web"""
    
    print("=== PRUEBA COMPLETA DE FILTROS DE MALLA CURRICULAR ===")
    
    base_url = "http://127.0.0.1:8001"
    malla_url = f"{base_url}/dashboard/malla-curricular/"
    
    # 1. Verificar datos disponibles
    print("1. Verificando datos disponibles...")
    print(f"   - Asignaturas válidas: {Asignatura.objects.exclude(nombre__regex=r'^\\d+$').count()}")
    print(f"   - Carreras: {Carrera.objects.count()}")
    print(f"   - Unidades: {UnidadAcademica.objects.count()}")
    
    # 2. Probar filtros uno por uno
    filtros_prueba = [
        {"descripcion": "Sin filtros (página principal)", "params": {}},
        {"descripcion": "Búsqueda por 'FISICA'", "params": {"search": "FISICA"}},
        {"descripcion": "Búsqueda por 'QUIMICA'", "params": {"search": "QUIMICA"}},
        {"descripcion": "Filtro por semestre 1", "params": {"semestre": "1"}},
        {"descripcion": "Filtro por semestre 2", "params": {"semestre": "2"}},
        {"descripcion": "Filtro por carrera ING_INDUSTRIAL", "params": {"carrera": "23"}},
        {"descripcion": "Filtro por UALP", "params": {"unidad_academica": "1"}},
        {"descripcion": "Búsqueda + Semestre", "params": {"search": "FISICA", "semestre": "1"}},
    ]
    
    print("\n2. Probando filtros en interfaz web...")
    
    for i, filtro in enumerate(filtros_prueba, 1):
        print(f"\n--- PRUEBA {i}: {filtro['descripcion']} ---")
        
        try:
            # Construir URL con parámetros
            if filtro['params']:
                query_string = "&".join([f"{k}={v}" for k, v in filtro['params'].items()])
                url = f"{malla_url}?{query_string}"
            else:
                url = malla_url
            
            print(f"URL: {url}")
            
            # Hacer petición (simular navegador)
            response = requests.get(url)
            
            if response.status_code == 200:
                content = response.text
                
                # Buscar indicadores en HTML
                if "asignaturas-grid" in content:
                    print("✅ Vista de resultados filtrados detectada")
                elif "carrera-card" in content:
                    print("✅ Vista de carreras por defecto detectada")
                else:
                    print("⚠️  Vista no reconocida")
                
                # Verificar contador de resultados
                if "Resultados de Búsqueda" in content:
                    print("✅ Sección de resultados filtrados presente")
                
                if "Filtros activos:" in content:
                    print("✅ Indicadores de filtros activos presentes")
                
                # Verificar si hay contenido
                if "No se encontraron" in content:
                    print("ℹ️  Sin resultados (puede ser normal)")
                else:
                    print("✅ Contenido encontrado")
                    
            elif response.status_code == 302:
                print("⚠️  Redirección (probablemente por autenticación)")
            else:
                print(f"❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5)  # Pausa entre requests
    
    print("\n3. Verificando funcionalidad AJAX...")
    
    # Probar endpoints AJAX
    ajax_tests = [
        {"url": f"{base_url}/dashboard/ajax/carreras-por-unidad/?unidad_id=1", "desc": "Carreras por unidad"},
        {"url": f"{base_url}/dashboard/ajax/asignaturas-por-carrera/?carrera_id=23", "desc": "Asignaturas por carrera"},
    ]
    
    for test in ajax_tests:
        try:
            response = requests.get(test['url'])
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {test['desc']}: {len(data.get('carreras', data.get('asignaturas', [])))} elementos")
            else:
                print(f"⚠️  {test['desc']}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {test['desc']}: Error {e}")

def verificar_integridad_datos():
    """Verificar que los datos estén limpios y correctos"""
    
    print("\n=== VERIFICACIÓN DE INTEGRIDAD DE DATOS ===")
    
    # 1. Verificar asignaturas limpias
    asignaturas_numericas = Asignatura.objects.filter(nombre__regex=r'^\\d+$')
    if asignaturas_numericas.exists():
        print(f"❌ Aún hay {asignaturas_numericas.count()} asignaturas con nombres numéricos:")
        for asig in asignaturas_numericas:
            print(f"   - ID {asig.id}: '{asig.nombre}'")
    else:
        print("✅ Sin asignaturas con nombres numéricos")
    
    # 2. Verificar distribución por carreras
    print(f"\n2. Distribución de asignaturas por carrera:")
    carreras_con_asignaturas = Carrera.objects.filter(
        asignatura__isnull=False
    ).distinct()
    
    for carrera in carreras_con_asignaturas:
        asig_count = Asignatura.objects.filter(
            carrera=carrera
        ).exclude(nombre__regex=r'^\\d+$').count()
        print(f"   - {carrera.nombre}: {asig_count} asignaturas válidas")
    
    # 3. Verificar semestres
    print(f"\n3. Distribución por semestre:")
    for sem in range(1, 11):
        count = Asignatura.objects.filter(
            semestre=sem
        ).exclude(nombre__regex=r'^\\d+$').count()
        if count > 0:
            print(f"   - Semestre {sem}: {count} asignaturas")

if __name__ == "__main__":
    verificar_integridad_datos()
    probar_filtros_completos()
    print("\n🎉 ¡PRUEBAS COMPLETADAS!")