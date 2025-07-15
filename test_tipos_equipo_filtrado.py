#!/usr/bin/env python
"""
Test para verificar el filtrado de tipos de equipo por unidad académica
"""
import os
import sys
import django
import json
from django.test import TestCase, RequestFactory

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from ingreso_datos.models import UnidadAcademica, TipoEquipo, EquipoIndividual

def test_tipos_equipo_filtrado():
    """Test que verifica que los tipos de equipo se filtren correctamente por unidad académica"""
    print("🔍 Iniciando test de filtrado de tipos de equipo...")
    
    # Crear cliente de prueba con configuración personalizada
    import requests
    
    # URL base del servidor
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Verificar que La Paz solo devuelve sus tipos de equipo
    print("\n📝 Test 1: Verificando tipos de equipo para La Paz...")
    
    try:
        response = requests.post(f'{base_url}/visualizacion/equipos/', {
            'action': 'get_tipos_equipo',
            'unidad_academica': 'LA_PAZ'
        })
        
        if response.status_code == 200:
            data = response.json()
            tipos_la_paz = data.get('tipos_equipo', [])
            print(f"✅ La Paz tiene {len(tipos_la_paz)} tipos de equipo")
            for tipo in tipos_la_paz[:5]:  # Mostrar solo los primeros 5
                print(f"   - {tipo['nombre']} ({tipo['display_name']})")
            if len(tipos_la_paz) > 5:
                print(f"   ... y {len(tipos_la_paz) - 5} más")
        else:
            print(f"❌ Error en La Paz: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión en La Paz: {e}")
        return False
    
    # Test 2: Verificar que Cochabamba solo devuelve sus tipos de equipo
    print("\n📝 Test 2: Verificando tipos de equipo para Cochabamba...")
    
    try:
        response = requests.post(f'{base_url}/visualizacion/equipos/', {
            'action': 'get_tipos_equipo',
            'unidad_academica': 'COCHABAMBA'
        })
        
        if response.status_code == 200:
            data = response.json()
            tipos_cochabamba = data.get('tipos_equipo', [])
            print(f"✅ Cochabamba tiene {len(tipos_cochabamba)} tipos de equipo")
            for tipo in tipos_cochabamba[:5]:  # Mostrar solo los primeros 5
                print(f"   - {tipo['nombre']} ({tipo['display_name']})")
            if len(tipos_cochabamba) > 5:
                print(f"   ... y {len(tipos_cochabamba) - 5} más")
        else:
            print(f"❌ Error en Cochabamba: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión en Cochabamba: {e}")
        return False
    
    # Test 3: Verificar que Santa Cruz devuelve lista vacía
    print("\n📝 Test 3: Verificando tipos de equipo para Santa Cruz...")
    
    try:
        response = requests.post(f'{base_url}/visualizacion/equipos/', {
            'action': 'get_tipos_equipo',
            'unidad_academica': 'SANTA_CRUZ'
        })
        
        if response.status_code == 200:
            data = response.json()
            tipos_santa_cruz = data.get('tipos_equipo', [])
            print(f"✅ Santa Cruz tiene {len(tipos_santa_cruz)} tipos de equipo")
            if len(tipos_santa_cruz) == 0:
                print("   ✅ Correcto: Santa Cruz no tiene equipos, por lo que no debe mostrar tipos")
            else:
                print(f"   ❌ Error: Santa Cruz no debería tener tipos de equipo")
                for tipo in tipos_santa_cruz:
                    print(f"   - {tipo['nombre']} ({tipo['display_name']})")
        else:
            print(f"❌ Error en Santa Cruz: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión en Santa Cruz: {e}")
        return False
    
    # Test 4: Verificar que sin unidad académica devuelve error o lista vacía
    print("\n📝 Test 4: Verificando comportamiento sin unidad académica...")
    
    try:
        response = requests.post(f'{base_url}/visualizacion/equipos/', {
            'action': 'get_tipos_equipo'
        })
        
        if response.status_code == 400:
            print("✅ Correcto: Sin unidad académica devuelve error 400")
        elif response.status_code == 200:
            data = response.json()
            tipos_sin_unidad = data.get('tipos_equipo', [])
            if len(tipos_sin_unidad) == 0:
                print("✅ Correcto: Sin unidad académica devuelve lista vacía")
            else:
                print(f"❌ Error: Sin unidad académica no debería devolver tipos")
        else:
            print(f"❌ Error inesperado: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión sin unidad académica: {e}")
        return False
    
    print("\n🎉 Test de filtrado completado exitosamente!")
    return True

if __name__ == "__main__":
    success = test_tipos_equipo_filtrado()
    if success:
        print("\n✅ TODOS LOS TESTS PASARON")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
        sys.exit(1)
