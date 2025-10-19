#!/usr/bin/env python3

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera

def verificar_limpieza_final():
    """Verificar que las asignaturas estén limpias y sin problemas"""
    
    print("=== VERIFICACIÓN FINAL DE ASIGNATURAS ===")
    
    # 1. Verificar que NO hay asignaturas con nombres numéricos
    asignaturas_numericas = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    print(f"1. Asignaturas con nombres numéricos: {asignaturas_numericas.count()}")
    
    if asignaturas_numericas.exists():
        print("❌ AÚN HAY PROBLEMAS:")
        for asig in asignaturas_numericas:
            print(f"   ID {asig.id}: '{asig.nombre}'")
    else:
        print("✅ Sin asignaturas con nombres numéricos")
    
    # 2. Verificar asignaturas de Ingeniería Industrial (la que sabemos tiene problemas)
    ing_industrial = Carrera.objects.filter(nombre__icontains='INDUSTRIAL').first()
    if ing_industrial:
        asignaturas_ing = Asignatura.objects.filter(carrera=ing_industrial)
        print(f"\n2. Asignaturas de Ingeniería Industrial: {asignaturas_ing.count()}")
        
        for asig in asignaturas_ing:
            if asig.nombre.isdigit():
                print(f"   ❌ PROBLEMÁTICA: ID {asig.id} = '{asig.nombre}'")
            else:
                print(f"   ✅ OK: ID {asig.id} = '{asig.nombre}'")
    
    # 3. Verificar que las asignaturas legítimas están bien
    asignaturas_legitimas = Asignatura.objects.filter(
        id__in=[168, 169, 171]
    )
    print(f"\n3. Asignaturas legítimas (IDs 168,169,171): {asignaturas_legitimas.count()}")
    for asig in asignaturas_legitimas:
        print(f"   ✅ ID {asig.id}: '{asig.nombre}' - {asig.carrera}")
    
    # 4. Contar total de asignaturas válidas
    total_asignaturas = Asignatura.objects.count()
    asignaturas_validas = Asignatura.objects.exclude(
        nombre__regex=r'^\d+$'
    ).count()
    
    print(f"\n4. Resumen:")
    print(f"   Total asignaturas: {total_asignaturas}")
    print(f"   Asignaturas válidas: {asignaturas_validas}")
    print(f"   Asignaturas problemáticas: {total_asignaturas - asignaturas_validas}")
    
    if total_asignaturas == asignaturas_validas:
        print("   🎉 ¡PERFECTO! Todas las asignaturas son válidas")
        return True
    else:
        print("   ⚠️  Aún hay asignaturas problemáticas")
        return False

if __name__ == "__main__":
    verificar_limpieza_final()