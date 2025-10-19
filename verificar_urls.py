#!/usr/bin/env python
"""
Script para verificar que todas las URLs están funcionando correctamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.urls import reverse, NoReverseMatch

def verificar_urls():
    print("🔗 VERIFICANDO URLS DE CORE")
    print("=" * 40)
    
    urls_core = [
        'core:dashboard',
        'core:malla_curricular', 
        'core:agregar_datos_malla',
        'core:detalle_asignatura'
    ]
    
    for url_name in urls_core:
        try:
            if 'detalle_asignatura' in url_name:
                # URL que requiere parámetro
                url = reverse(url_name, kwargs={'asignatura_id': 169})
                print(f"   ✅ {url_name}: {url}")
            else:
                # URLs sin parámetros
                url = reverse(url_name)
                print(f"   ✅ {url_name}: {url}")
        except NoReverseMatch as e:
            print(f"   ❌ {url_name}: ERROR - {e}")
        except Exception as e:
            print(f"   ⚠️ {url_name}: PROBLEMA - {e}")
    
    print(f"\n🎯 VERIFICACIÓN ESPECÍFICA:")
    
    # Verificar específicamente la URL problemática
    try:
        url_problematica = reverse('core:agregar_datos_malla')
        print(f"   ✅ URL 'core:agregar_datos_malla' resuelve a: {url_problematica}")
    except Exception as e:
        print(f"   ❌ URL 'core:agregar_datos_malla' FALLA: {e}")
    
    # Verificar template
    try:
        from django.template.loader import get_template
        template = get_template('core/detalle_asignatura.html')
        print(f"   ✅ Template 'core/detalle_asignatura.html' cargado correctamente")
    except Exception as e:
        print(f"   ❌ Template 'core/detalle_asignatura.html' FALLA: {e}")

if __name__ == "__main__":
    verificar_urls()