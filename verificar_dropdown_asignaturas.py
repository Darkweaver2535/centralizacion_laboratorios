#!/usr/bin/env python
"""
Script para verificar las asignaturas que aparecen en el dropdown
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_asignaturas_dropdown():
    print("🔍 VERIFICANDO ASIGNATURAS EN DROPDOWN")
    print("=" * 50)
    
    # Simular la lógica de la vista AJAX
    print(f"\n📚 TODAS LAS ASIGNATURAS EN BASE DE DATOS:")
    
    todas_asignaturas = Asignatura.objects.all()
    
    for asignatura in todas_asignaturas:
        print(f"   ID: {asignatura.id} | Nombre: '{asignatura.nombre}' | Carrera: {asignatura.carrera}")
    
    print(f"\n🔍 APLICANDO FILTROS DE LA VISTA AJAX:")
    
    # Aplicar los mismos filtros que la vista AJAX
    asignaturas_filtradas = []
    asignaturas_ocultas = []
    
    for asignatura in todas_asignaturas:
        display_name = asignatura.get_nombre_display()
        
        # FILTRO 1: Omitir asignaturas con nombres problemáticos
        es_numerica = asignatura.nombre.isdigit()
        es_muy_corta = len(asignatura.nombre.strip()) <= 3
        tiene_solo_numeros = asignatura.nombre.replace(' ', '').isdigit()
        
        if es_numerica or (es_muy_corta and tiene_solo_numeros):
            asignaturas_ocultas.append((asignatura, "Nombre problemático (numérico/muy corto)"))
            continue
        
        # FILTRO 2: Omitir asignaturas con nombres confusos
        nombres_similares = ['168', '169', '170', '171', '172', '173', '174', '175']
        if asignatura.nombre in nombres_similares:
            asignaturas_ocultas.append((asignatura, "Nombre confuso (ID como nombre)"))
            continue
        
        # Si pasa todos los filtros, se incluye
        display_text = display_name
        if asignatura.sigla_curricular:
            display_text += f" ({asignatura.sigla_curricular})"
        
        asignaturas_filtradas.append((asignatura, display_text))
    
    print(f"\n✅ ASIGNATURAS QUE APARECERÁN EN EL DROPDOWN ({len(asignaturas_filtradas)}):")
    for asignatura, display_text in asignaturas_filtradas:
        print(f"   👁️ '{display_text}' (ID interno: {asignatura.id})")
    
    print(f"\n🙈 ASIGNATURAS OCULTAS ({len(asignaturas_ocultas)}):")
    for asignatura, razon in asignaturas_ocultas:
        print(f"   🔕 '{asignatura.nombre}' - {razon}")
    
    # Verificar específicamente UALP
    print(f"\n🎯 VERIFICACIÓN ESPECÍFICA - UALP:")
    
    ualp = UnidadAcademica.objects.filter(id=1).first()
    if ualp:
        carreras_ualp = Carrera.objects.filter(unidad_academica=ualp)
        
        for carrera in carreras_ualp[:3]:  # Solo las primeras 3
            asignaturas_carrera = Asignatura.objects.filter(carrera=carrera)
            asignaturas_visibles = [a for a, _ in asignaturas_filtradas if a.carrera == carrera]
            
            print(f"   📚 {carrera.nombre}:")
            print(f"      Total asignaturas: {asignaturas_carrera.count()}")
            print(f"      Visibles en dropdown: {len(asignaturas_visibles)}")
            
            for asig in asignaturas_visibles[:2]:  # Mostrar solo las primeras 2
                print(f"         - {asig.get_nombre_display()}")
    
    print(f"\n🎉 RESULTADO ESPERADO:")
    print(f"   👁️ Solo aparecerán nombres descriptivos (ej: FISICA I, QUIMICA GENERAL)")
    print(f"   🙈 NO aparecerán números como 168, 169, 170, 171")
    print(f"   ✨ El dropdown se verá limpio y profesional")

if __name__ == "__main__":
    verificar_asignaturas_dropdown()