#!/usr/bin/env python3
"""
Script para crear guías de laboratorio para TODAS las unidades académicas
El problema es que solo UACB tiene guías, las otras 4 unidades no tienen ninguna.
"""

import os
import django
import random
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, UnidadTematica, GuiaLaboratorio, Practica

def crear_guias_para_todas_unidades():
    """Crear guías de laboratorio para todas las unidades académicas que no las tienen"""
    
    print("🚀 Iniciando creación de guías para todas las unidades académicas...")
    
    # Plantillas de guías (nombres genéricos aplicables a cualquier materia)
    plantillas_guias = [
        "Fundamentos Prácticos",
        "Actividades de Laboratorio", 
        "Ejercicios Aplicados",
        "Casos de Estudio",
        "Proyectos Prácticos",
        "Análisis Experimental",
        "Desarrollo de Competencias",
        "Evaluación Práctica",
        "Metodología Aplicada",
        "Resolución de Problemas"
    ]
    
    # Plantillas de prácticas
    plantillas_practicas = [
        "Práctica Introductoria",
        "Práctica de Desarrollo", 
        "Práctica de Evaluación",
        "Análisis de Casos",
        "Ejercicio Aplicado",
        "Proyecto Integrador",
        "Evaluación Experimental",
        "Metodología Práctica",
        "Resolución de Problemas",
        "Síntesis Final"
    ]
    
    # Obtener unidades académicas sin guías
    unidades_sin_guias = []
    for unidad in UnidadAcademica.objects.all():
        guias_count = GuiaLaboratorio.objects.filter(
            unidad_tematica__asignatura__carrera__unidad_academica=unidad
        ).count()
        if guias_count == 0:
            unidades_sin_guias.append(unidad)
    
    print(f"📊 Unidades sin guías encontradas: {len(unidades_sin_guias)}")
    for unidad in unidades_sin_guias:
        print(f"   - {unidad.nombre}")
    
    total_guias_creadas = 0
    total_practicas_creadas = 0
    
    for unidad in unidades_sin_guias:
        print(f"\n🏛️  Procesando {unidad.nombre}...")
        
        # Obtener todas las unidades temáticas de esta unidad académica
        unidades_tematicas = UnidadTematica.objects.filter(
            asignatura__carrera__unidad_academica=unidad
        )
        
        print(f"   📚 Unidades temáticas encontradas: {unidades_tematicas.count()}")
        
        guias_esta_unidad = 0
        practicas_esta_unidad = 0
        
        # Crear guías para 1 de cada 10 unidades temáticas (igual que UACB)
        unidades_seleccionadas = list(unidades_tematicas)[::10]  # Cada 10
        
        for i, unidad_tematica in enumerate(unidades_seleccionadas):
            # Crear guía de laboratorio
            nombre_guia = random.choice(plantillas_guias)
            
            guia = GuiaLaboratorio.objects.create(
                unidad_tematica=unidad_tematica,
                nombre=nombre_guia,
                numero=i + 1,
                descripcion=f"Guía práctica para {unidad_tematica.nombre}"
            )
            guias_esta_unidad += 1
            
            # Crear 3 prácticas para cada guía
            for j in range(3):
                nombre_practica = random.choice(plantillas_practicas)
                
                practica = Practica.objects.create(
                    guia_laboratorio=guia,
                    nombre=nombre_practica,
                    numero=j + 1,
                    descripcion=f"Práctica {j+1} para {nombre_guia}"
                )
                practicas_esta_unidad += 1
        
        print(f"   ✅ Creadas {guias_esta_unidad} guías y {practicas_esta_unidad} prácticas")
        total_guias_creadas += guias_esta_unidad
        total_practicas_creadas += practicas_esta_unidad
    
    print(f"\n🎉 PROCESO COMPLETADO")
    print(f"📈 Total de guías creadas: {total_guias_creadas}")
    print(f"📈 Total de prácticas creadas: {total_practicas_creadas}")
    
    # Verificación final
    print(f"\n📊 VERIFICACIÓN FINAL:")
    for unidad in UnidadAcademica.objects.all():
        guias_count = GuiaLaboratorio.objects.filter(
            unidad_tematica__asignatura__carrera__unidad_academica=unidad
        ).count()
        print(f"   {unidad.nombre}: {guias_count} guías")

if __name__ == "__main__":
    crear_guias_para_todas_unidades()
