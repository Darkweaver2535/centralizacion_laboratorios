#!/usr/bin/env python3
"""
Script para corregir inconsistencias entre carreras y asignaturas en equipos
Crea asignaturas de laboratorio para todas las carreras
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, Asignatura
from equipos.models import Equipo

def crear_asignaturas_laboratorio_para_carreras():
    """Crear asignaturas de laboratorio básicas para todas las carreras"""
    
    # Asignaturas de laboratorio básicas que deberían estar en todas las carreras
    asignaturas_laboratorio = [
        ('fisica_i', 'Física I', 1),
        ('quimica_general', 'Química General', 1),
        ('fisica_ii', 'Física II', 2),
        ('fisicoquimica', 'Fisicoquímica', 3),
        ('matematica_i', 'Matemática I', 1),  # También agregar matemática
        ('matematica_ii', 'Matemática II', 2),
    ]
    
    carreras = Carrera.objects.all()
    asignaturas_creadas = 0
    
    print(f"📚 CREANDO ASIGNATURAS PARA {carreras.count()} CARRERAS...")
    print()
    
    for carrera in carreras:
        print(f"🎓 Procesando: {carrera}")
        
        for nombre, display_name, semestre in asignaturas_laboratorio:
            # Verificar si la asignatura ya existe para esta carrera
            asignatura_existente = Asignatura.objects.filter(
                nombre=nombre, 
                carrera=carrera, 
                semestre=semestre
            ).first()
            
            if not asignatura_existente:
                # Crear la asignatura
                nueva_asignatura = Asignatura.objects.create(
                    nombre=nombre,
                    carrera=carrera,
                    semestre=semestre,
                    carga_horaria_semanal=4,
                    carga_horaria_semestral=80,
                    codigo_competencia=f"{carrera.nombre}_{nombre}_{semestre}",
                    sigla_curricular=nombre.upper().replace('_', '')
                )
                asignaturas_creadas += 1
                print(f"  ✅ Creada: {display_name}")
            else:
                print(f"  ⭐ Ya existe: {display_name}")
    
    print()
    print(f"🎉 RESUMEN:")
    print(f"   Asignaturas creadas: {asignaturas_creadas}")
    print(f"   Total asignaturas ahora: {Asignatura.objects.count()}")

def corregir_equipos_sin_asignaturas():
    """Asignar asignaturas a equipos que no tienen"""
    
    print()
    print("🔧 CORRIGIENDO EQUIPOS SIN ASIGNATURAS...")
    
    equipos_sin_asignatura = Equipo.objects.filter(asignatura__isnull=True)
    print(f"Equipos sin asignatura: {equipos_sin_asignatura.count()}")
    
    equipos_corregidos = 0
    
    for equipo in equipos_sin_asignatura:
        if equipo.carrera:
            # Buscar una asignatura de laboratorio para esta carrera
            asignatura_fisica = Asignatura.objects.filter(
                carrera=equipo.carrera,
                nombre='fisica_i'
            ).first()
            
            if asignatura_fisica:
                equipo.asignatura = asignatura_fisica
                equipo.save()
                equipos_corregidos += 1
    
    print(f"Equipos corregidos: {equipos_corregidos}")

def verificar_consistencia():
    """Verificar que no haya inconsistencias carrera-asignatura"""
    
    print()
    print("🔍 VERIFICANDO CONSISTENCIA...")
    
    equipos_inconsistentes = []
    for equipo in Equipo.objects.filter(asignatura__isnull=False):
        if equipo.carrera and equipo.asignatura:
            if equipo.asignatura.carrera != equipo.carrera:
                equipos_inconsistentes.append(equipo)
    
    print(f"Equipos con inconsistencias: {len(equipos_inconsistentes)}")
    
    if equipos_inconsistentes:
        print("Primeros 5 equipos inconsistentes:")
        for equipo in equipos_inconsistentes[:5]:
            print(f"  - {equipo.equipo_existente[:30]}...")
            print(f"    Carrera equipo: {equipo.carrera}")
            print(f"    Carrera asignatura: {equipo.asignatura.carrera}")

if __name__ == "__main__":
    print("🚀 INICIANDO CORRECCIÓN DE ASIGNATURAS...")
    print("=" * 60)
    
    # Paso 1: Crear asignaturas de laboratorio para todas las carreras
    crear_asignaturas_laboratorio_para_carreras()
    
    # Paso 2: Corregir equipos sin asignaturas
    corregir_equipos_sin_asignaturas()
    
    # Paso 3: Verificar consistencia
    verificar_consistencia()
    
    print()
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
