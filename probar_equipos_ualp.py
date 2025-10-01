#!/usr/bin/env python3
"""
Script para probar la funcionalidad de carga de equipos UALP
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica

def probar_vista_equipos_ualp():
    """Simular la lógica de la vista AJAX"""
    
    print("🧪 PROBANDO LÓGICA DE VISTA AJAX EQUIPOS UALP")
    print("=" * 50)
    
    # Filtrar equipos de la UALP
    ualp = UnidadAcademica.objects.filter(nombre='UALP').first()
    if not ualp:
        print("❌ No se encontró la UALP")
        return
    
    print(f"✅ UALP encontrada: {ualp}")
    
    # Simular búsqueda sin filtro
    equipos_query = Equipo.objects.filter(unidad_academica=ualp)
    print(f"📊 Total equipos en UALP: {equipos_query.count()}")
    
    # Obtener equipos únicos por nombre (evitar duplicados)
    equipos = equipos_query.values('equipo_existente', 'marca', 'modelo', 'estado').distinct()[:10]
    
    print("\n📋 PRIMEROS 10 EQUIPOS ÚNICOS:")
    equipos_data = []
    for i, equipo in enumerate(equipos, 1):
        # Crear texto descriptivo
        texto = equipo['equipo_existente']
        if equipo['marca'] and equipo['marca'] != 'Por definir':
            texto += f" - {equipo['marca']}"
        if equipo['modelo'] and equipo['modelo'] != 'Por definir':
            texto += f" ({equipo['modelo']})"
        
        print(f"{i}. {texto}")
        print(f"   Estado: {equipo['estado']}")
        
        equipos_data.append({
            'id': equipo['equipo_existente'],
            'text': texto,
            'estado': equipo['estado']
        })
    
    print(f"\n✅ Se pueden cargar {len(equipos_data)} equipos en el select")
    
    # Probar con filtro de búsqueda
    print("\n🔍 PROBANDO BÚSQUEDA CON FILTRO 'MONITOR':")
    equipos_filtrados = equipos_query.filter(
        equipo_existente__icontains='monitor'
    ).values('equipo_existente', 'marca', 'modelo', 'estado').distinct()[:5]
    
    for equipo in equipos_filtrados:
        texto = equipo['equipo_existente']
        if equipo['marca'] and equipo['marca'] != 'Por definir':
            texto += f" - {equipo['marca']}"
        print(f"- {texto}")

if __name__ == "__main__":
    probar_vista_equipos_ualp()
