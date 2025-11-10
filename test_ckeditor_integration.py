#!/usr/bin/env python3

"""
Script de prueba para verificar que CKEditor está funcionando correctamente
en los campos especificados del formulario de agregar datos de malla curricular.
"""

import os
import sys
import django
import requests
from bs4 import BeautifulSoup

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

def test_ckeditor_integration():
    """Prueba la integración de CKEditor en el formulario"""
    
    print("🔍 Verificando integración de CKEditor...")
    
    try:
        # Hacer request a la página del formulario
        url = 'http://127.0.0.1:8000/dashboard/malla-curricular/agregar-datos/'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Página cargada correctamente")
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Verificar que CKEditor CDN está presente
            ckeditor_scripts = soup.find_all('script', src=lambda x: x and 'ckeditor' in x)
            if ckeditor_scripts:
                print("✅ CDN de CKEditor encontrado")
                for script in ckeditor_scripts:
                    print(f"   📦 {script.get('src')}")
            else:
                print("❌ CDN de CKEditor NO encontrado")
            
            # Verificar campos con clase ckeditor-field
            ckeditor_fields = soup.find_all('textarea', class_='ckeditor-field')
            print(f"\n📝 Campos con CKEditor encontrados: {len(ckeditor_fields)}")
            
            expected_fields = [
                'fundamento_teorico',
                'procedimientos', 
                'calculos_resultados',
                'cuestionario'
            ]
            
            found_fields = []
            for field in ckeditor_fields:
                name = field.get('name', '')
                for expected in expected_fields:
                    if expected in name:
                        if expected not in found_fields:
                            found_fields.append(expected)
                        print(f"   ✅ {expected}: {name}")
                        break
            
            # Verificar que todos los campos esperados están presentes
            missing_fields = [field for field in expected_fields if field not in found_fields]
            if missing_fields:
                print(f"\n⚠️ Campos faltantes: {missing_fields}")
            else:
                print(f"\n🎉 Todos los campos esperados tienen CKEditor: {found_fields}")
            
            # Verificar función de inicialización
            page_content = response.text
            if 'initializeCKEditor' in page_content:
                print("✅ Función initializeCKEditor encontrada")
            else:
                print("❌ Función initializeCKEditor NO encontrada")
            
            if 'ClassicEditor.create' in page_content:
                print("✅ Código de inicialización de ClassicEditor encontrado")
            else:
                print("❌ Código de inicialización de ClassicEditor NO encontrado")
            
        else:
            print(f"❌ Error al cargar la página: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Asegúrate de que esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_models_ckeditor():
    """Verifica que los modelos tengan campos CKEditor"""
    
    print("\n🗄️ Verificando modelos con CKEditor...")
    
    from core.models import FundamentoTeorico, Procedimientos, CalculosResultados, Cuestionario
    from django_ckeditor_5.fields import CKEditor5Field
    
    models_to_check = [
        (FundamentoTeorico, ['contenido']),
        (Procedimientos, ['descripcion']),
        (CalculosResultados, ['procedimiento_calculo']),
        (Cuestionario, ['pregunta', 'respuesta_esperada'])
    ]
    
    for model_class, field_names in models_to_check:
        print(f"\n📋 Modelo: {model_class.__name__}")
        for field_name in field_names:
            try:
                field = model_class._meta.get_field(field_name)
                if isinstance(field, CKEditor5Field):
                    print(f"   ✅ {field_name}: CKEditor5Field")
                else:
                    print(f"   ⚠️ {field_name}: {type(field).__name__} (no es CKEditor5Field)")
            except:
                print(f"   ❌ {field_name}: Campo no encontrado")

if __name__ == '__main__':
    test_ckeditor_integration()
    test_models_ckeditor()
    
    print("\n🚀 Prueba completada!")
    print("\n📝 Para verificar manualmente:")
    print("1. Ve a: http://127.0.0.1:8000/dashboard/malla-curricular/agregar-datos/")
    print("2. Llena los campos básicos hasta llegar a 'Grupos Adicionales'")
    print("3. Haz clic en 'Agregar Grupo de Datos Adicionales'")
    print("4. Verifica que los campos tengan la barra de herramientas de CKEditor")
    print("5. Prueba insertar imágenes, formatear texto, etc.")