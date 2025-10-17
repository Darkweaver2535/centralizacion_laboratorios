#!/usr/bin/env python3
"""
Script para identificar y limpiar asignaturas problemáticas en la base de datos
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera, UnidadAcademica

def identificar_asignaturas_problematicas():
    """Identificar asignaturas con nombres problemáticos"""
    print("🔍 Buscando asignaturas problemáticas...")
    
    # Buscar asignaturas que son solo números
    asignaturas_numericas = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    print(f"📊 Encontradas {asignaturas_numericas.count()} asignaturas con nombres solo numéricos:")
    
    for asig in asignaturas_numericas:
        print(f"  - ID: {asig.id} | Nombre: '{asig.nombre}' | Carrera: {asig.carrera} | Semestre: {asig.semestre}")
        
        # Buscar si hay duplicados con nombres similares
        similares = Asignatura.objects.filter(
            carrera=asig.carrera,
            semestre=asig.semestre
        ).exclude(id=asig.id)
        
        if similares.exists():
            print(f"    🔄 Posibles duplicados en la misma carrera y semestre:")
            for sim in similares:
                print(f"      - ID: {sim.id} | Nombre: '{sim.nombre}'")
    
    # Buscar asignaturas que pueden ser "Física II" u otras similares
    fisica_asignaturas = Asignatura.objects.filter(nombre__icontains='fisica')
    print(f"\n🔬 Asignaturas de Física encontradas ({fisica_asignaturas.count()}):")
    for asig in fisica_asignaturas:
        print(f"  - ID: {asig.id} | Nombre: '{asig.nombre}' | Carrera: {asig.carrera}")
    
    return asignaturas_numericas

def corregir_asignaturas_problematicas():
    """Corregir o eliminar asignaturas problemáticas"""
    asignaturas_numericas = identificar_asignaturas_problematicas()
    
    if not asignaturas_numericas.exists():
        print("✅ No se encontraron asignaturas problemáticas.")
        return
    
    print(f"\n🛠️  Procediendo a corregir {asignaturas_numericas.count()} asignaturas problemáticas...")
    
    for asig in asignaturas_numericas:
        print(f"\n📋 Procesando asignatura ID {asig.id}: '{asig.nombre}'")
        
        # Intentar determinar qué asignatura debería ser basándose en el contexto
        if asig.nombre == '170':
            # Buscar si hay una "Física II" en la misma carrera y semestre
            fisica_ii = Asignatura.objects.filter(
                carrera=asig.carrera,
                semestre=asig.semestre,
                nombre__icontains='fisica'
            ).exclude(id=asig.id).first()
            
            if fisica_ii:
                print(f"  🔬 Parece ser un duplicado de Física II (ID: {fisica_ii.id})")
                print(f"  🗑️  Eliminando asignatura duplicada...")
                asig.delete()
                print(f"  ✅ Asignatura '{asig.nombre}' eliminada exitosamente")
            else:
                # Si no hay duplicado claro, renombrar a algo más descriptivo
                nuevo_nombre = 'fisica_ii'
                print(f"  ⚠️  Sin duplicado claro encontrado. Renombrando a '{nuevo_nombre}'")
                asig.nombre = nuevo_nombre
                asig.save()
                print(f"  ✅ Asignatura renombrada a '{nuevo_nombre}'")
        else:
            # Para otros números, simplemente eliminar si son claramente inválidos
            print(f"  🗑️  Eliminando asignatura con nombre inválido '{asig.nombre}'...")
            asig.delete()
            print(f"  ✅ Asignatura eliminada exitosamente")

def verificar_carreras_ualp_industrial():
    """Verificar específicamente las asignaturas de UALP - Ingeniería Industrial"""
    print("\n🏭 Verificando asignaturas de UALP - Ingeniería Industrial...")
    
    try:
        ualp = UnidadAcademica.objects.get(nombre='UALP')
        print(f"✅ Unidad académica encontrada: {ualp}")
        
        # Buscar todas las carreras de UALP para ver cuáles hay
        todas_carreras = Carrera.objects.filter(unidad_academica=ualp)
        print(f"📋 Carreras disponibles en UALP ({todas_carreras.count()}):")
        for carrera in todas_carreras:
            print(f"  - {carrera.nombre}: {carrera.get_nombre_display()}")
        
        # Buscar específicamente Ingeniería Industrial (no Agroindustrial)
        ing_industrial = Carrera.objects.filter(
            unidad_academica=ualp,
            nombre='ING_INDUSTRIAL'  # Buscar por el código exacto
        ).first()
        
        if ing_industrial:
            print(f"\n🏭 ✅ Carrera de Ingeniería Industrial encontrada: {ing_industrial.get_nombre_display()}")
            asignaturas = Asignatura.objects.filter(carrera=ing_industrial).order_by('semestre', 'nombre')
            
            print(f"📚 Total de asignaturas: {asignaturas.count()}")
            
            # Identificar asignaturas problemáticas específicamente
            problematicas = []
            for asig in asignaturas:
                es_problematica = asig.nombre.isdigit() or len(asig.nombre.strip()) < 3
                if es_problematica:
                    problematicas.append(asig)
                    print(f"  ⚠️  PROBLEMÁTICA - Semestre {asig.semestre}: '{asig.nombre}' (ID: {asig.id})")
                else:
                    print(f"  ✅ Semestre {asig.semestre}: {asig.nombre} (ID: {asig.id})")
            
            return ing_industrial, problematicas
                
        else:
            print("❌ No se encontró la carrera ING_INDUSTRIAL en UALP")
            return None, []
            
    except UnidadAcademica.DoesNotExist:
        print("❌ No se encontró la unidad académica UALP")
        return None, []

def limpiar_asignaturas_especificas(carrera, asignaturas_problematicas):
    """Limpiar asignaturas problemáticas específicas"""
    if not asignaturas_problematicas:
        print("✅ No hay asignaturas problemáticas para limpiar")
        return
    
    print(f"\n🛠️  Limpiando {len(asignaturas_problematicas)} asignaturas problemáticas...")
    
    for asig in asignaturas_problematicas:
        print(f"\n🗑️  Eliminando asignatura problemática: ID {asig.id} - '{asig.nombre}'")
        asig.delete()
        print(f"  ✅ Eliminada exitosamente")

if __name__ == '__main__':
    print("=" * 60)
    print("🧹 LIMPIEZA DE ASIGNATURAS PROBLEMÁTICAS")
    print("🎯 Foco: UALP - Ingeniería Industrial")
    print("=" * 60)
    
    # Verificar el caso específico de Ingeniería Industrial
    carrera, asignaturas_problematicas = verificar_carreras_ualp_industrial()
    
    if carrera and asignaturas_problematicas:
        print(f"\n⚠️  Se encontraron {len(asignaturas_problematicas)} asignaturas problemáticas en {carrera.get_nombre_display()}")
        
        # Ejecutar limpieza automáticamente
        print("🔧 Procediendo con la limpieza automática...")
        limpiar_asignaturas_especificas(carrera, asignaturas_problematicas)
        print("\n🎉 Limpieza completada!")
        
        # Verificar resultado
        print("\n🔍 Verificando resultado...")
        carrera_post, problematicas_post = verificar_carreras_ualp_industrial()
        if not problematicas_post:
            print("✅ ¡Todas las asignaturas problemáticas han sido eliminadas!")
        else:
            print(f"⚠️  Aún quedan {len(problematicas_post)} asignaturas problemáticas")
            
    elif carrera:
        print(f"\n✅ No se encontraron asignaturas problemáticas en {carrera.get_nombre_display()}")
    else:
        print("\n❌ No se pudo encontrar la carrera de Ingeniería Industrial")
    
    print("\n" + "=" * 60)