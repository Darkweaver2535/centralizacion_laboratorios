#!/usr/bin/env python3
"""
Probar el endpoint AJAX de asignaturas para verificar el filtrado
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera
from django.http import HttpRequest

def probar_ajax_asignaturas():
    """Probar el endpoint AJAX que debería filtrar asignaturas problemáticas"""
    
    print("🔍 PROBANDO FILTRO AJAX DE ASIGNATURAS")
    print("=" * 50)
    
    # 1. Verificar todas las asignaturas de Ingeniería Industrial
    print("\n1. 📚 ASIGNATURAS DE INGENIERÍA INDUSTRIAL:")
    try:
        ing_industrial = Carrera.objects.get(nombre='ING_INDUSTRIAL')
        asignaturas = Asignatura.objects.filter(carrera=ing_industrial).order_by('id')
        
        print(f"   🎓 Carrera: {ing_industrial.get_nombre_display()}")
        print(f"   📊 Total asignaturas: {asignaturas.count()}")
        
        for asig in asignaturas:
            es_problematica = asig.nombre.isdigit()
            icono = "⚠️" if es_problematica else "✅"
            display_name = asig.get_nombre_display()
            
            print(f"   {icono} ID {asig.id}: '{asig.nombre}' → Display: '{display_name}'")
            
            # Verificar si el display name es igual al nombre y es numérico
            if display_name == asig.nombre and asig.nombre.isdigit():
                print(f"      🚨 ESTA ASIGNATURA DEBERÍA SER FILTRADA")
        
        print(f"\n2. 🔍 SIMULANDO ENDPOINT AJAX:")
        
        # Simular la lógica del endpoint
        asignaturas_filtradas = []
        asignaturas_omitidas = []
        
        for asignatura in asignaturas:
            display_name = asignatura.get_nombre_display()
            
            # APLICAR EL FILTRO: Si el display_name es igual al nombre y el nombre es numérico, omitir
            if display_name == asignatura.nombre and asignatura.nombre.isdigit():
                print(f"   ❌ OMITIENDO: ID {asignatura.id} '{asignatura.nombre}' (problemática)")
                asignaturas_omitidas.append(asignatura)
                continue  # Omitir esta asignatura problemática
            
            # Agregar a la lista filtrada
            asignaturas_filtradas.append(asignatura)
            print(f"   ✅ INCLUYENDO: ID {asignatura.id} '{display_name}'")
        
        print(f"\n3. 📊 RESULTADOS DEL FILTRADO:")
        print(f"   ✅ Asignaturas incluidas: {len(asignaturas_filtradas)}")
        print(f"   ❌ Asignaturas omitidas: {len(asignaturas_omitidas)}")
        
        if asignaturas_omitidas:
            print(f"\n   🚨 ASIGNATURAS PROBLEMÁTICAS DETECTADAS:")
            for asig in asignaturas_omitidas:
                print(f"      - ID {asig.id}: '{asig.nombre}' (debería estar filtrada)")
        
        print(f"\n4. 🔧 VERIFICACIÓN DEL ENDPOINT REAL:")
        print(f"   URL: /dashboard/ajax/asignaturas-por-carrera/?carrera_id={ing_industrial.id}")
        
    except Carrera.DoesNotExist:
        print("   ❌ No se encontró carrera Ingeniería Industrial")
    
    return True

if __name__ == "__main__":
    probar_ajax_asignaturas()