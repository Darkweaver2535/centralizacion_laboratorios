#!/usr/bin/env python3
"""
Script para agregar datos de ejemplo usando los modelos existentes
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from ingreso_datos.models import Carrera, Asignatura

def main():
    print("🚀 Agregando datos de ejemplo para guías de laboratorio...")
    
    # Carreras disponibles en el modelo
    carreras_disponibles = [
        'ingenieria_sistemas',
        'ingenieria_civil', 
        'ingenieria_sistemas_electronicos',
        'ingenieria_comercial',
        'ingenieria_ambiental',
        'ingenieria_agroindustrial'
    ]
    
    carreras_creadas = 0
    asignaturas_creadas = 0
    
    # Crear carreras
    for carrera_nombre in carreras_disponibles:
        carrera, created = Carrera.objects.get_or_create(
            nombre=carrera_nombre,
            defaults={
                'descripcion': f'Carrera de {dict(Carrera.CARRERAS)[carrera_nombre]}'
            }
        )
        
        if created:
            carreras_creadas += 1
            print(f"✅ Carrera creada: {carrera}")
        else:
            print(f"📋 Carrera existente: {carrera}")
    
    # Crear asignaturas para cada carrera y semestre
    for carrera in Carrera.objects.all():
        for semestre in range(1, 9):  # 8 semestres
            asignaturas_semestre = Asignatura.get_asignaturas_por_semestre(semestre)
            
            if not asignaturas_semestre:
                continue
                
            # Tomar las primeras 3-5 asignaturas por semestre para cada carrera
            import random
            num_asignaturas = min(len(asignaturas_semestre), random.randint(3, 5))
            asignaturas_seleccionadas = random.sample(asignaturas_semestre, num_asignaturas)
            
            for asignatura_codigo, asignatura_nombre in asignaturas_seleccionadas:
                asignatura, created = Asignatura.objects.get_or_create(
                    nombre=asignatura_codigo,
                    carrera=carrera,
                    semestre=semestre,
                    defaults={
                        'carga_horaria_semanal': random.randint(4, 8),
                        'carga_horaria_semestral': random.randint(64, 128)
                    }
                )
                
                if created:
                    asignaturas_creadas += 1
    
    print(f"\n🎉 Datos agregados exitosamente:")
    print(f"   📚 Carreras: {carreras_creadas} nuevas")
    print(f"   📖 Asignaturas: {asignaturas_creadas} nuevas")
    print(f"   🎯 Total carreras: {Carrera.objects.count()}")
    print(f"   🎯 Total asignaturas: {Asignatura.objects.count()}")
    
    # Mostrar resumen por carrera
    print("\n📊 Resumen por carrera:")
    for carrera in Carrera.objects.all():
        total_asignaturas = Asignatura.objects.filter(carrera=carrera).count()
        print(f"   - {carrera}: {total_asignaturas} asignaturas")
        
        # Mostrar algunas asignaturas de ejemplo
        asignaturas_ejemplo = Asignatura.objects.filter(carrera=carrera)[:3]
        for asignatura in asignaturas_ejemplo:
            print(f"     * {asignatura.get_nombre_display()} ({asignatura.semestre}° sem)")

if __name__ == "__main__":
    main()
