#!/usr/bin/env python3
"""
Script específico para limpiar asignaturas problemáticas de Ingeniería Industrial UALP
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera, UnidadAcademica

def main():
    print("=" * 70)
    print("🧹 LIMPIEZA DE ASIGNATURAS PROBLEMÁTICAS")
    print("🎯 UALP - Ingeniería Industrial")
    print("=" * 70)
    
    # Obtener la carrera específica
    try:
        carrera = Carrera.objects.get(id=23)  # ID 23 = ING_INDUSTRIAL en UALP
        print(f"✅ Carrera encontrada: {carrera.get_nombre_display()}")
        print(f"   Unidad: {carrera.unidad_academica}")
        print(f"   ID: {carrera.id}")
        
        # Obtener todas las asignaturas
        asignaturas = Asignatura.objects.filter(carrera=carrera).order_by('semestre', 'nombre')
        print(f"\n📚 Total de asignaturas: {asignaturas.count()}")
        
        # Identificar problemáticas
        problematicas = []
        normales = []
        
        print(f"\n📋 Lista de asignaturas:")
        for asig in asignaturas:
            # Detectar si es problemática
            es_problematica = (
                asig.nombre.isdigit() or  # Solo números como "170"
                len(asig.nombre.strip()) <= 3 or  # Muy corto
                asig.nombre.strip() in ['170', '171', '172', '173', '174', '175']  # Números específicos
            )
            
            if es_problematica:
                problematicas.append(asig)
                print(f"  ⚠️  PROBLEMÁTICA: ID {asig.id} - '{asig.nombre}' - Semestre {asig.semestre}")
            else:
                normales.append(asig)
                print(f"  ✅ Válida: ID {asig.id} - '{asig.nombre}' - Semestre {asig.semestre}")
        
        print(f"\n📊 Resumen:")
        print(f"  ✅ Asignaturas válidas: {len(normales)}")
        print(f"  ⚠️  Asignaturas problemáticas: {len(problematicas)}")
        
        # Limpiar problemáticas
        if problematicas:
            print(f"\n🛠️  Procediendo a eliminar {len(problematicas)} asignaturas problemáticas...")
            
            for asig in problematicas:
                print(f"  🗑️  Eliminando: ID {asig.id} - '{asig.nombre}'")
                asig.delete()
                print(f"     ✅ Eliminada exitosamente")
            
            print(f"\n🎉 Limpieza completada!")
            
            # Verificar resultado
            asignaturas_final = Asignatura.objects.filter(carrera=carrera).count()
            print(f"📈 Asignaturas restantes: {asignaturas_final}")
            
        else:
            print(f"\n✅ No hay asignaturas problemáticas que limpiar")
        
    except Carrera.DoesNotExist:
        print("❌ Error: No se encontró la carrera con ID 23")
    
    print(f"\n" + "=" * 70)

if __name__ == '__main__':
    main()