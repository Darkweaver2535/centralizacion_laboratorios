#!/usr/bin/env python3
"""
Script simple para probar la vista AJAX de equipos UALP
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

def probar_vista_simple():
    """Probar solo la lógica de la vista AJAX"""
    
    print("🔍 PROBANDO VISTA AJAX DE EQUIPOS UALP")
    print("=" * 50)
    
    # Importar la función de la vista directamente
    from equipos.views import cargar_equipos_ualp_ajax
    from django.http import HttpRequest
    from core.models import UnidadAcademica
    from equipos.models import Equipo
    
    # Verificar datos
    ualp = UnidadAcademica.objects.filter(nombre='UALP').first()
    if ualp:
        equipos_count = Equipo.objects.filter(unidad_academica=ualp).count()
        print(f"✅ Equipos en UALP: {equipos_count}")
        
        # Simular request sin query
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {}
        
        # Simular usuario autenticado (necesario para @login_required)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Buscar usuario existente
        usuario_existente = User.objects.first()
        if usuario_existente:
            request.user = usuario_existente
            
            try:
                response = cargar_equipos_ualp_ajax(request)
                
                if response.status_code == 200:
                    import json
                    data = json.loads(response.content.decode())
                    equipos = data.get('equipos', [])
                    
                    print(f"✅ Vista AJAX exitosa: {len(equipos)} equipos")
                    
                    # Mostrar algunos ejemplos
                    print("\n📋 PRIMEROS 5 EQUIPOS:")
                    for i, equipo in enumerate(equipos[:5]):
                        print(f"{i+1}. {equipo['text']}")
                        print(f"   Estado: {equipo['estado']}")
                        print()
                    
                    # Probar con query
                    request.GET = {'query': 'MONITOR'}
                    response_filtrado = cargar_equipos_ualp_ajax(request)
                    
                    if response_filtrado.status_code == 200:
                        data_filtrado = json.loads(response_filtrado.content.decode())
                        equipos_filtrados = data_filtrado.get('equipos', [])
                        print(f"✅ Filtro 'MONITOR': {len(equipos_filtrados)} equipos")
                        
                        if equipos_filtrados:
                            print(f"Ejemplo: {equipos_filtrados[0]['text']}")
                
                else:
                    print(f"❌ Error: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error ejecutando vista: {e}")
        else:
            print("❌ No hay usuarios en el sistema")
    else:
        print("❌ No se encontró UALP")

if __name__ == "__main__":
    probar_vista_simple()
