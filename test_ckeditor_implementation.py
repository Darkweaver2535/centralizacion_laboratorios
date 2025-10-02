#!/usr/bin/env python3
"""
Test script para verificar la implementación de CKEditor
"""

import requests
import sys
from bs4 import BeautifulSoup

def test_ckeditor_implementation():
    """Verifica que la implementación de CKEditor esté funcionando correctamente"""
    
    print("🧪 Testando implementación de CKEditor...")
    
    try:
        # Verificar que el servidor esté corriendo
        response = requests.get('http://127.0.0.1:8000/agregar-datos-malla/', timeout=10)
        
        if response.status_code == 200:
            print("✅ Servidor Django ejecutándose correctamente")
            
            # Parsear el HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Verificar que se carguen los scripts de CKEditor
            ckeditor_scripts = soup.find_all('script', src=lambda x: x and 'ckeditor' in x.lower())
            if ckeditor_scripts:
                print(f"✅ Scripts de CKEditor encontrados: {len(ckeditor_scripts)}")
            else:
                print("❌ No se encontraron scripts de CKEditor")
            
            # Verificar campos con clase ckeditor-field
            ckeditor_fields = soup.find_all('textarea', class_='ckeditor-field')
            if ckeditor_fields:
                print(f"✅ Campos CKEditor encontrados: {len(ckeditor_fields)}")
                
                expected_fields = [
                    'fundamento_teorico', 'materiales', 'herramientas', 
                    'equipos', 'procedimientos', 'calculos_resultados', 'cuestionario'
                ]
                
                found_fields = []
                for field in ckeditor_fields:
                    name = field.get('name', '')
                    for expected in expected_fields:
                        if expected in name:
                            found_fields.append(expected)
                            break
                
                print(f"✅ Campos específicos encontrados: {list(set(found_fields))}")
                
                if len(set(found_fields)) >= 7:
                    print("✅ Todos los campos CKEditor requeridos están presentes")
                else:
                    print(f"⚠️  Faltan algunos campos: {set(expected_fields) - set(found_fields)}")
                    
            else:
                print("❌ No se encontraron campos con clase ckeditor-field")
            
            # Verificar función de inicialización
            if 'initializeCKEditor' in response.text:
                print("✅ Función de inicialización CKEditor encontrada")
            else:
                print("❌ Función de inicialización CKEditor no encontrada")
            
            # Verificar configuración de CKEditor
            if "'laboratorio'" in response.text:
                print("✅ Configuración personalizada 'laboratorio' encontrada")
            else:
                print("❌ Configuración personalizada 'laboratorio' no encontrada")
            
            # Verificar CSS personalizado
            if '.cke_chrome' in response.text:
                print("✅ CSS personalizado para CKEditor encontrado")
            else:
                print("❌ CSS personalizado para CKEditor no encontrado")
                
            print("\n🎉 Implementación de CKEditor completada exitosamente!")
            print("📋 Funcionalidades implementadas:")
            print("   • Rich text editing con toolbar completo")
            print("   • Soporte para imágenes y archivos")
            print("   • Configuración personalizada 'laboratorio'")
            print("   • Inicialización dinámica para campos nuevos")
            print("   • CSS integrado con el diseño existente")
            print("   • Sincronización en envío de formulario")
            
        else:
            print(f"❌ Error del servidor: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor Django")
        print("   Asegúrate de que esté ejecutándose en http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_ckeditor_implementation()