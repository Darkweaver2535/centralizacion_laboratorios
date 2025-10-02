#!/usr/bin/env python3
"""
Script para probar CKEditor implementación
"""

import requests
import time

def test_ckeditor_implementation():
    """Probar que CKEditor se está cargando correctamente"""
    
    print("🧪 Probando implementación de CKEditor...")
    
    try:
        # Dar tiempo a que el servidor se inicie
        time.sleep(2)
        
        # Verificar que el formulario se carga
        response = requests.get('http://127.0.0.1:8001/dashboard/malla-curricular/agregar-datos/', timeout=10)
        
        if response.status_code == 200:
            print("✅ Formulario carga correctamente")
            text = response.text
            
            # Verificar que CKEditor CDN se está cargando
            if 'cdn.ckeditor.com' in text:
                print("✅ CKEditor CDN encontrado")
            else:
                print("❌ CKEditor CDN NO encontrado")
            
            # Verificar clase ckeditor-field
            if 'ckeditor-field' in text:
                print("✅ Campos CKEditor encontrados")
                
                # Contar campos
                count = text.count('ckeditor-field')
                print(f"📊 Número de campos CKEditor: {count}")
            else:
                print("❌ Campos CKEditor NO encontrados")
            
            # Verificar función de inicialización
            if 'initializeCKEditor' in text:
                print("✅ Función de inicialización encontrada")
            else:
                print("❌ Función de inicialización NO encontrada")
            
            # Verificar configuración específica
            if 'waitForCKEditor' in text:
                print("✅ Función de espera de carga encontrada")
            else:
                print("❌ Función de espera de carga NO encontrada")
                
            # Verificar campos específicos
            fields = ['fundamento_teorico', 'materiales', 'herramientas', 'equipos', 'procedimientos', 'calculos_resultados', 'cuestionario']
            found_fields = []
            for field in fields:
                if field in text:
                    found_fields.append(field)
            
            print(f"✅ Campos específicos encontrados: {len(found_fields)}/7")
            print(f"   Campos: {found_fields}")
            
            if len(found_fields) >= 7:
                print("🎉 ¡TODOS los campos CKEditor están presentes!")
                print("📋 Para activar CKEditor:")
                print("   1. Abrir el formulario en el navegador")
                print("   2. Hacer clic en 'Agregar Grupo de Datos Adicionales'")
                print("   3. Los campos con texto enriquecido deberían aparecer automáticamente")
                print("   4. Buscar campos: Fundamento Teórico, Materiales, Herramientas, etc.")
            else:
                missing = set(fields) - set(found_fields)
                print(f"⚠️  Faltan campos: {missing}")
            
        else:
            print(f"❌ Error del servidor: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor Django")
        print("   Asegúrate de que esté corriendo en http://127.0.0.1:8001")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_ckeditor_implementation()