#!/usr/bin/env python3
"""
Script para corregir las asignaturas de los equipos para que coincidan con su carrera
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, Asignatura
from equipos.models import Equipo

def corregir_asignaturas_equipos():
    """Corregir las asignaturas de los equipos para que coincidan con su carrera"""
    
    print("🔧 CORRIGIENDO ASIGNATURAS DE EQUIPOS...")
    print()
    
    equipos_inconsistentes = []
    
    # Encontrar todos los equipos con inconsistencias
    for equipo in Equipo.objects.filter(asignatura__isnull=False):
        if equipo.carrera and equipo.asignatura:
            if equipo.asignatura.carrera != equipo.carrera:
                equipos_inconsistentes.append(equipo)
    
    print(f"Equipos con inconsistencias encontrados: {len(equipos_inconsistentes)}")
    
    equipos_corregidos = 0
    errores = 0
    
    for equipo in equipos_inconsistentes:
        try:
            # Obtener el nombre de la asignatura actual
            nombre_asignatura_actual = equipo.asignatura.nombre
            
            # Buscar la misma asignatura pero para la carrera del equipo
            asignatura_correcta = Asignatura.objects.filter(
                nombre=nombre_asignatura_actual,
                carrera=equipo.carrera
            ).first()
            
            if asignatura_correcta:
                # Actualizar el equipo con la asignatura correcta
                equipo.asignatura = asignatura_correcta
                equipo.save()
                equipos_corregidos += 1
                
                if equipos_corregidos <= 5:  # Mostrar solo los primeros 5
                    print(f"✅ Corregido: {equipo.equipo_existente[:40]}...")
                    print(f"   Carrera: {equipo.carrera}")
                    print(f"   Nueva asignatura: {asignatura_correcta}")
                    print()
            else:
                errores += 1
                if errores <= 3:  # Mostrar solo los primeros 3 errores
                    print(f"❌ No se encontró asignatura '{nombre_asignatura_actual}' para carrera '{equipo.carrera}'")
        
        except Exception as e:
            errores += 1
            if errores <= 3:
                print(f"❌ Error procesando equipo {equipo.id}: {str(e)}")
    
    print(f"📊 RESUMEN:")
    print(f"   Equipos corregidos: {equipos_corregidos}")
    print(f"   Errores: {errores}")
    
    return equipos_corregidos, errores

def verificar_resultado():
    """Verificar que se hayan corregido las inconsistencias"""
    
    print()
    print("🔍 VERIFICACIÓN FINAL...")
    
    equipos_inconsistentes = []
    for equipo in Equipo.objects.filter(asignatura__isnull=False):
        if equipo.carrera and equipo.asignatura:
            if equipo.asignatura.carrera != equipo.carrera:
                equipos_inconsistentes.append(equipo)
    
    print(f"Equipos con inconsistencias restantes: {len(equipos_inconsistentes)}")
    
    if len(equipos_inconsistentes) == 0:
        print("🎉 ¡Todas las inconsistencias han sido corregidas!")
    else:
        print("⚠️  Aún quedan algunas inconsistencias por resolver")
        
        # Mostrar algunos ejemplos
        print("Ejemplos de inconsistencias restantes:")
        for equipo in equipos_inconsistentes[:3]:
            print(f"  - {equipo.equipo_existente[:30]}...")
            print(f"    Carrera equipo: {equipo.carrera}")
            print(f"    Carrera asignatura: {equipo.asignatura.carrera}")
            print(f"    Asignatura: {equipo.asignatura.nombre}")

def mostrar_estadisticas_finales():
    """Mostrar estadísticas finales de asignaturas por carrera"""
    
    print()
    print("📈 ESTADÍSTICAS FINALES:")
    print()
    
    for carrera in Carrera.objects.all():
        asignaturas_count = Asignatura.objects.filter(carrera=carrera).count()
        equipos_count = Equipo.objects.filter(carrera=carrera, asignatura__isnull=False).count()
        print(f"🎓 {carrera}:")
        print(f"   Asignaturas: {asignaturas_count}")
        print(f"   Equipos con asignatura: {equipos_count}")
        
        # Mostrar las asignaturas disponibles
        asignaturas = Asignatura.objects.filter(carrera=carrera)
        if asignaturas.exists():
            print(f"   Materias disponibles:")
            for asignatura in asignaturas:
                print(f"     - {asignatura.get_nombre_display()}")
        print()

if __name__ == "__main__":
    print("🚀 INICIANDO CORRECCIÓN DE ASIGNATURAS EN EQUIPOS...")
    print("=" * 70)
    
    # Paso 1: Corregir asignaturas de equipos
    equipos_corregidos, errores = corregir_asignaturas_equipos()
    
    # Paso 2: Verificar resultado
    verificar_resultado()
    
    # Paso 3: Mostrar estadísticas finales
    mostrar_estadisticas_finales()
    
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
