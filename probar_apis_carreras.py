#!/usr/bin/env python
"""
Script para probar las APIs de carreras y verificar que funcionen correctamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera
import requests
import json

def probar_apis_carreras():
    """Prueba todas las APIs de carreras con diferentes formatos"""
    
    base_url = "http://127.0.0.1:8001"
    
    print("🔗 PRUEBA DE APIs DE CARRERAS")
    print("=" * 35)
    
    # Obtener unidades académicas de la base de datos
    unidades = UnidadAcademica.objects.all().order_by('nombre')
    
    print(f"📊 Unidades académicas en BD: {unidades.count()}")
    for unidad in unidades:
        carreras_count = Carrera.objects.filter(unidad_academica=unidad).count()
        print(f"   • {unidad.nombre} (ID: {unidad.id}): {carreras_count} carreras")
    print()
    
    # Probar API principal con IDs numéricos
    print("🧪 PRUEBA 1: API Principal con IDs numéricos")
    print("-" * 45)
    
    for unidad in unidades:
        url = f"{base_url}/api/carreras/?unidad_academica={unidad.id}"
        print(f"📍 Probando: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {unidad.nombre}: {len(data)} carreras encontradas")
                if data:
                    print(f"      Ejemplo: {data[0]['nombre']}")
            else:
                print(f"   ❌ {unidad.nombre}: Error {response.status_code}")
                print(f"      Respuesta: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ {unidad.nombre}: Error de conexión - {str(e)}")
        print()
    
    # Probar API principal con nombres de texto
    print("🧪 PRUEBA 2: API Principal con nombres de texto")
    print("-" * 48)
    
    mapeo_nombres = {
        'la_paz': 'UALP',
        'santa_cruz': 'UASC', 
        'cochabamba': 'UACB',
        'riberalta': 'UCRB',
        'tropico': 'UATP'
    }
    
    for nombre_frontend, nombre_bd in mapeo_nombres.items():
        url = f"{base_url}/api/carreras/?unidad_academica={nombre_frontend}"
        print(f"📍 Probando: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ '{nombre_frontend}' → {nombre_bd}: {len(data)} carreras encontradas")
                if data:
                    print(f"      Ejemplo: {data[0]['nombre']}")
            else:
                print(f"   ❌ '{nombre_frontend}' → {nombre_bd}: Error {response.status_code}")
                print(f"      Respuesta: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ '{nombre_frontend}' → {nombre_bd}: Error de conexión - {str(e)}")
        print()
    
    # Probar API de insumos
    print("🧪 PRUEBA 3: API de Insumos")
    print("-" * 25)
    
    for unidad in unidades[:2]:  # Solo las primeras 2 para no saturar
        url = f"{base_url}/insumos/api/carreras/?unidad_academica={unidad.id}"
        print(f"📍 Probando: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'carreras' in data:
                    print(f"   ✅ {unidad.nombre}: {len(data['carreras'])} carreras encontradas")
                    if data['carreras']:
                        print(f"      Ejemplo: {data['carreras'][0]['nombre']}")
                else:
                    print(f"   ⚠️ {unidad.nombre}: Formato de respuesta inesperado")
            else:
                print(f"   ❌ {unidad.nombre}: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ {unidad.nombre}: Error de conexión - {str(e)}")
        print()

def verificar_frontend_carreras():
    """Verifica que el frontend pueda cargar carreras"""
    print("🌐 VERIFICACIÓN DEL FRONTEND")
    print("=" * 30)
    
    base_url = "http://127.0.0.1:8001"
    
    # Probar página de nuevo equipo
    try:
        url = f"{base_url}/equipos/nuevo/"
        print(f"📍 Probando página: {url}")
        
        response = requests.get(url)
        if response.status_code == 200:
            print("   ✅ Página de nuevo equipo carga correctamente")
            if 'unidad_academica' in response.text:
                print("   ✅ Campo de unidad académica encontrado")
            if 'carrera' in response.text:
                print("   ✅ Campo de carrera encontrado")
        else:
            print(f"   ❌ Error cargando página: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
    
    print()

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO COMPLETO DE APIs DE CARRERAS")
    print("🏛️  Sistema EMI - Centralización de Laboratorios")
    print("=" * 55)
    print()
    
    try:
        probar_apis_carreras()
        verificar_frontend_carreras()
        
        print("✅ DIAGNÓSTICO COMPLETADO")
        print("💡 Si todas las pruebas son exitosas, las carreras deberían aparecer en el frontend")
        
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {str(e)}")
        print("🔧 Verificar que el servidor Django esté ejecutándose en el puerto 8001")
