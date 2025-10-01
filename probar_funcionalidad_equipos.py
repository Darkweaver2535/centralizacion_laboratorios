#!/usr/bin/env python3
"""
Script para probar completamente la funcionalidad de equipos UALP
"""

import os
import django
import requests
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

def probar_funcionalidad_completa():
    """Probar toda la funcionalidad de equipos UALP"""
    
    print("🔍 PROBANDO FUNCIONALIDAD COMPLETA DE EQUIPOS UALP")
    print("=" * 60)
    
    # 1. Verificar datos en la base de datos
    from equipos.models import Equipo
    from core.models import UnidadAcademica
    
    ualp = UnidadAcademica.objects.filter(nombre='UALP').first()
    if not ualp:
        print("❌ Error: No se encontró la UALP")
        return
    
    equipos_count = Equipo.objects.filter(unidad_academica=ualp).count()
    print(f"✅ Base de datos: {equipos_count} equipos en UALP")
    
    # 2. Probar la vista AJAX
    from django.test import Client
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Crear cliente y usuario de prueba
    client = Client()
    user, created = User.objects.get_or_create(username='test_user', defaults={
        'email': 'test@test.com',
        'first_name': 'Test',
        'last_name': 'User'
    })
    
    if created:
        user.set_password('test123')
        user.save()
    
    # Login
    client.login(username='test_user', password='test123')
    
    # Probar la vista AJAX sin filtro
    response = client.get('/equipos/ajax/cargar-equipos-ualp/')
    
    if response.status_code == 200:
        data = response.json()
        equipos = data.get('equipos', [])
        print(f"✅ Vista AJAX: {len(equipos)} equipos cargados")
        
        # Mostrar algunos ejemplos
        print("\n📋 EJEMPLOS DE EQUIPOS CARGADOS:")
        for i, equipo in enumerate(equipos[:5]):
            print(f"{i+1}. ID: '{equipo['id']}'")
            print(f"   Texto: '{equipo['text']}'")
            print(f"   Estado: {equipo['estado']}")
            print()
        
        # Probar con filtro
        response_filtrado = client.get('/equipos/ajax/cargar-equipos-ualp/', {'query': 'MONITOR'})
        if response_filtrado.status_code == 200:
            data_filtrado = response_filtrado.json()
            equipos_filtrados = data_filtrado.get('equipos', [])
            print(f"✅ Filtro 'MONITOR': {len(equipos_filtrados)} equipos encontrados")
            
            if equipos_filtrados:
                print("Ejemplo con filtro:")
                print(f"- {equipos_filtrados[0]['text']}")
        
    else:
        print(f"❌ Error en vista AJAX: {response.status_code}")
        print(f"Contenido: {response.content.decode()}")
    
    # 3. Verificar que el formulario puede mostrar un equipo
    print(f"\n📝 PROBANDO ACCESO A FORMULARIO DE EDICIÓN:")
    
    # Obtener un equipo para editar
    equipo_ejemplo = Equipo.objects.first()
    if equipo_ejemplo:
        response_form = client.get(f'/equipos/{equipo_ejemplo.id}/editar/')
        if response_form.status_code == 200:
            print(f"✅ Formulario de edición accesible: /equipos/{equipo_ejemplo.id}/editar/")
            # Verificar que el campo equipo_requerido esté en el HTML
            if 'id_equipo_requerido' in response_form.content.decode():
                print("✅ Campo 'equipo_requerido' presente en el formulario")
            else:
                print("❌ Campo 'equipo_requerido' no encontrado en el formulario")
        else:
            print(f"❌ Error accediendo al formulario: {response_form.status_code}")
    
    print("\n🎉 PRUEBA COMPLETADA")

if __name__ == "__main__":
    probar_funcionalidad_completa()
