#!/usr/bin/env python3

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura

def eliminar_asignaturas_numericas():
    """Eliminar completamente las asignaturas con nombres puramente numéricos"""
    
    print("=== ELIMINANDO ASIGNATURAS CON NOMBRES NUMÉRICOS ===")
    
    # Buscar asignaturas con nombres puramente numéricos
    asignaturas_numericas = Asignatura.objects.filter(
        nombre__regex=r'^\d+$'
    )
    
    print(f"Asignaturas con nombres numéricos encontradas: {asignaturas_numericas.count()}")
    
    for asig in asignaturas_numericas:
        print(f"  ID {asig.id}: '{asig.nombre}' - Carrera: {asig.carrera}")
    
    if asignaturas_numericas.exists():
        print("\n¿Eliminar estas asignaturas? (Escriba 'SI' para confirmar)")
        confirmacion = input().strip()
        
        if confirmacion.upper() == 'SI':
            eliminadas = asignaturas_numericas.count()
            asignaturas_numericas.delete()
            print(f"✅ {eliminadas} asignaturas eliminadas exitosamente")
        else:
            print("❌ Operación cancelada")
    else:
        print("✅ No hay asignaturas con nombres numéricos para eliminar")
    
    print("\n=== VERIFICANDO RESULTADO ===")
    
    # Verificar que no queden
    restantes = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    print(f"Asignaturas con nombres numéricos restantes: {restantes.count()}")
    
    # Mostrar las asignaturas problemáticas que AÚN tienen nombres legítimos
    asignaturas_ids_problematicos = Asignatura.objects.filter(
        id__in=[168, 169, 171]
    )
    
    print(f"\nAsignaturas con IDs 168, 169, 171 (pero nombres legítimos):")
    for asig in asignaturas_ids_problematicos:
        print(f"  ID {asig.id}: '{asig.nombre}' - Esta ES válida pero tiene ID confuso")

if __name__ == "__main__":
    eliminar_asignaturas_numericas()