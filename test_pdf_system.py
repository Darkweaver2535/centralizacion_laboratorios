#!/usr/bin/env python3
"""
Test simple del sistema de PDF de guías
"""
import os
import django
import requests

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from usuarios.models import Usuario
from django.test import Client

def probar_sistema_pdf():
    print("=== PRUEBA DEL SISTEMA PDF DE GUÍAS ===")
    
    # Crear cliente
    client = Client()
    
    # Crear usuario si no existe
    if not Usuario.objects.filter(correo_institucional='test@umsa.bo').exists():
        user = Usuario(
            correo_institucional='test@umsa.bo',
            nombres='Test',
            apellidos='Usuario',
        )
        user.set_password('test123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ Usuario creado: test@umsa.bo")
    else:
        user = Usuario.objects.get(correo_institucional='test@umsa.bo')
        print(f"✅ Usuario existente: {user.correo_institucional}")
    
    # Hacer login
    login_success = client.login(username='test@umsa.bo', password='test123')
    print(f"🔐 Login exitoso: {login_success}")
    
    if not login_success:
        print("❌ Error en el login - probando login directo")
        return
    
    print("\n📊 PROBANDO VISTA DE GUÍAS...")
    response = client.get('/visualizacion/?categoria=guias')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Vista de guías funciona")
        
        print("\n📄 PROBANDO GENERACIÓN DE PDF...")
        # Probar generar PDF para práctica ID 22 (FINITO)
        pdf_response = client.get('/guias/practica/22/generar-pdf/')
        print(f"PDF Status Code: {pdf_response.status_code}")
        
        if pdf_response.status_code == 200:
            print("✅ PDF generado exitosamente")
            print(f"📏 Tamaño del PDF: {len(pdf_response.content)} bytes")
            print(f"📑 Content-Type: {pdf_response.get('Content-Type', 'N/A')}")
            
            # Guardar PDF para verificar
            with open('/tmp/test_guia.pdf', 'wb') as f:
                f.write(pdf_response.content)
            print(f"💾 PDF guardado en: /tmp/test_guia.pdf")
            
        else:
            print(f"❌ Error generando PDF: {pdf_response.status_code}")
            if hasattr(pdf_response, 'content'):
                print(f"Error content: {pdf_response.content.decode()[:200]}")
                
        print("\n🔍 PROBANDO VISTA DE DETALLES...")
        detalle_response = client.get('/guias/practica/22/detalle/')
        print(f"Detalle Status Code: {detalle_response.status_code}")
        
        if detalle_response.status_code == 200:
            print("✅ Vista de detalles funciona")
        else:
            print(f"❌ Error en detalles: {detalle_response.status_code}")
    
    print(f"\n🌐 CREDENCIALES PARA BROWSER:")
    print(f"   Email: test@umsa.bo")
    print(f"   Password: test123")
    print(f"   URL Login: http://127.0.0.1:8000/login/")
    print(f"   URL Guías: http://127.0.0.1:8000/visualizacion/?categoria=guias")
    print(f"   URL PDF Directo: http://127.0.0.1:8000/guias/practica/22/generar-pdf/")

if __name__ == "__main__":
    probar_sistema_pdf()