#!/usr/bin/env python3
"""
Script de prueba para verificar la integración completa del sistema de guías PDF
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import PracticaLaboratorio
from guias.plantilla_utils import crear_guia_temporal_desde_practica, generar_guia_pdf_desde_plantilla
from usuarios.models import Usuario
from django.contrib.auth.models import AnonymousUser

def test_plantilla_integration():
    """Probar la integración completa de plantillas"""
    
    print("🧪 === PRUEBA DE INTEGRACIÓN DE GUÍAS PDF ===")
    
    # 1. Verificar que existe al menos una práctica
    practicas = PracticaLaboratorio.objects.all()
    print(f"📊 Prácticas encontradas: {practicas.count()}")
    
    if not practicas.exists():
        print("❌ No hay prácticas disponibles para probar")
        return False
    
    # 2. Tomar la primera práctica
    practica = practicas.first()
    print(f"📋 Probando con práctica: {practica.nombre}")
    
    # 3. Verificar que existe un usuario para la prueba
    try:
        user = Usuario.objects.first()
        if not user:
            print("⚠️ No hay usuarios, creando usuario temporal")
            user = Usuario.objects.create_user(
                username='test_temp',
                email='test@emi.edu.bo',
                password='testpass123'
            )
    except Exception as e:
        print(f"❌ Error con usuario: {e}")
        return False
    
    # 4. Crear guía temporal
    try:
        print("🔄 Creando guía temporal...")
        guia_temporal = crear_guia_temporal_desde_practica(practica, user)
        print(f"✅ Guía temporal creada: {guia_temporal.titulo}")  # Usar titulo en lugar de nombre_guia
    except Exception as e:
        print(f"❌ Error creando guía temporal: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Verificar plantilla
    plantilla_path = Path(__file__).parent / 'templates' / 'core' / 'plantilla_emi_manual_corregida.docx'
    print(f"📁 Ruta plantilla: {plantilla_path}")
    print(f"📄 Plantilla existe: {plantilla_path.exists()}")
    
    if plantilla_path.exists():
        size = plantilla_path.stat().st_size
        print(f"📏 Tamaño plantilla: {size:,} bytes")
    
    # 6. Generar documento
    try:
        print("🔄 Generando documento...")
        buffer, file_type = generar_guia_pdf_desde_plantilla(guia_temporal)
        
        if buffer and file_type != 'error':
            size = len(buffer.getvalue())
            print(f"✅ Documento generado exitosamente")
            print(f"📏 Tamaño del archivo: {size:,} bytes")
            print(f"📋 Tipo de archivo: {file_type.upper()}")
            
            # Verificar contenido
            content = buffer.getvalue()
            if file_type == 'pdf' and content.startswith(b'%PDF'):
                print("✅ Archivo PDF válido detectado")
            elif file_type == 'docx' and b'PK' in content[:10]:
                print("✅ Archivo DOCX válido detectado")
            else:
                print("⚠️ Tipo de archivo no pudo ser verificado completamente")
            
            return True
        else:
            print(f"❌ Error generando documento: {file_type}")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_simulation():
    """Simular una llamada al endpoint"""
    
    print("\n🌐 === SIMULACIÓN DE ENDPOINT ===")
    
    # Obtener primera práctica
    practica = PracticaLaboratorio.objects.first()
    if not practica:
        print("❌ No hay prácticas para probar endpoint")
        return False
    
    print(f"🎯 Simulando llamada: /guias/practica/{practica.id}/generar-pdf/")
    
    try:
        from django.test import RequestFactory
        from guias.views import generar_practica_pdf
        from django.contrib.auth.models import AnonymousUser
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.get(f'/guias/practica/{practica.id}/generar-pdf/')
        request.user = Usuario.objects.first() or AnonymousUser()
        
        # Llamar a la vista
        response = generar_practica_pdf(request, practica.id)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Content-Type: {response.get('Content-Type', 'No definido')}")
        print(f"📁 Content-Disposition: {response.get('Content-Disposition', 'No definido')}")
        
        if hasattr(response, 'content'):
            size = len(response.content)
            print(f"📏 Tamaño respuesta: {size:,} bytes")
            
            if size > 0:
                print("✅ Endpoint funcionando correctamente")
                return True
            else:
                print("❌ Respuesta vacía")
                return False
        else:
            print("❌ No hay contenido en la respuesta")
            return False
            
    except Exception as e:
        print(f"❌ Error simulando endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 Iniciando pruebas de integración...\n")
    
    success1 = test_plantilla_integration()
    success2 = test_endpoint_simulation()
    
    print(f"\n📊 === RESUMEN ===")
    print(f"✅ Integración plantilla: {'PASS' if success1 else 'FAIL'}")
    print(f"🌐 Simulación endpoint: {'PASS' if success2 else 'FAIL'}")
    
    if success1 and success2:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente.")
        print("🔗 Puedes probar en: http://127.0.0.1:8000/visualizacion/?categoria=guias")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    sys.exit(0 if (success1 and success2) else 1)