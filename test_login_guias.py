#!/usr/bin/env python3
"""
Script para probar el login y las guías directamente
"""
import os
import django
import requests
from django.test import Client
from django.contrib.auth.models import User

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

def test_guias_view():
    print("=== PROBANDO VISTA DE GUÍAS ===")
    
    # Crear cliente de Django para testing
    client = Client()
    
    # Crear superusuario si no existe
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        print(f"✅ Superusuario creado: admin / admin123")
    else:
        user = User.objects.get(username='admin')
        print(f"✅ Usuario existente: {user.username}")
    
    # Hacer login
    login_success = client.login(username='admin', password='admin123')
    print(f"🔐 Login exitoso: {login_success}")
    
    if not login_success:
        print("❌ Error en el login")
        return
    
    # Probar la vista de guías
    print("\n📋 Probando vista de guías...")
    response = client.get('/visualizacion/?categoria=guias')
    
    print(f"📄 Status Code: {response.status_code}")
    print(f"📦 Template usado: {response.templates[0].name if response.templates else 'N/A'}")
    
    if response.status_code == 200:
        print("✅ Vista de guías carga correctamente")
        
        # Verificar contexto
        context = response.context
        if context:
            print(f"\n📊 DATOS DEL CONTEXTO:")
            print(f"   - Categoría: {context.get('categoria')}")
            print(f"   - Items: {len(context.get('items', []))}")
            print(f"   - Guías: {len(context.get('guias', []))}")
            print(f"   - Stats: {context.get('stats', {})}")
            
            # Mostrar algunas guías
            guias = context.get('items', [])
            if guias:
                print(f"\n🧪 PRÁCTICAS ENCONTRADAS ({len(guias)}):")
                for i, practica in enumerate(guias[:3], 1):
                    print(f"   {i}. {practica.nombre}")
                    print(f"      - Carrera: {practica.contenido_analitico.unidad_didactica.asignatura.carrera}")
                    print(f"      - Asignatura: {practica.contenido_analitico.unidad_didactica.asignatura.nombre}")
                    print(f"      - Semestre: {practica.contenido_analitico.unidad_didactica.asignatura.semestre}°")
                if len(guias) > 3:
                    print(f"   ... y {len(guias)-3} más")
            else:
                print("   ⚠️  No se encontraron prácticas")
                
    else:
        print(f"❌ Error al cargar la vista: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"Error: {response.content.decode()[:500]}")

if __name__ == "__main__":
    test_guias_view()
    print(f"\n🌐 URL para probar: http://127.0.0.1:8000/visualizacion/?categoria=guias")