#!/usr/bin/env python3
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadTematica, GuiaLaboratorio, Practica

def crear_guias_y_practicas_inteligente():
    print("=== CREANDO GUÍAS DE LABORATORIO Y PRÁCTICAS (CANTIDAD RAZONABLE) ===")
    
    # Solo crear para un subconjunto de unidades temáticas (no todas)
    # Seleccionar 1 de cada 10 unidades temáticas para ser eficientes
    total_unidades = UnidadTematica.objects.count()
    unidades_seleccionadas = UnidadTematica.objects.filter(id__in=[
        unidad.id for i, unidad in enumerate(UnidadTematica.objects.all()) 
        if i % 10 == 0  # Solo 1 de cada 10
    ])
    
    print(f"Total unidades temáticas: {total_unidades}")
    print(f"Unidades seleccionadas para guías: {unidades_seleccionadas.count()}")
    
    # Plantillas de guías por tipo de materia
    guias_templates = {
        'matematica': [
            {'nombre': 'Ejercicios de Cálculo', 'descripcion': 'Resolución de problemas matemáticos'},
            {'nombre': 'Laboratorio de Funciones', 'descripcion': 'Análisis gráfico de funciones'},
        ],
        'fisica': [
            {'nombre': 'Experimentos de Mecánica', 'descripcion': 'Prácticas de laboratorio físico'},
            {'nombre': 'Mediciones y Análisis', 'descripcion': 'Técnicas de medición experimental'},
        ],
        'quimica': [
            {'nombre': 'Reacciones en Laboratorio', 'descripcion': 'Experimentos químicos básicos'},
            {'nombre': 'Análisis Cualitativo', 'descripcion': 'Identificación de compuestos'},
        ],
        'programacion': [
            {'nombre': 'Ejercicios de Codificación', 'descripcion': 'Desarrollo de algoritmos'},
            {'nombre': 'Proyectos Prácticos', 'descripcion': 'Implementación de sistemas'},
        ],
        'default': [
            {'nombre': 'Actividades Prácticas', 'descripcion': 'Ejercicios aplicados de la materia'},
            {'nombre': 'Casos de Estudio', 'descripcion': 'Análisis de casos reales'},
        ]
    }
    
    # Plantillas de prácticas
    practicas_templates = [
        {'nombre': 'Práctica Introductoria', 'descripcion': 'Conceptos básicos y preparación'},
        {'nombre': 'Práctica de Desarrollo', 'descripcion': 'Aplicación de conocimientos'},
        {'nombre': 'Práctica de Evaluación', 'descripcion': 'Consolidación y evaluación'},
    ]
    
    total_guias_creadas = 0
    total_practicas_creadas = 0
    
    for unidad in unidades_seleccionadas:
        # Determinar tipo de materia
        nombre_asignatura = unidad.asignatura.nombre.lower()
        
        if any(palabra in nombre_asignatura for palabra in ['matematica', 'calculo']):
            guias_template = guias_templates['matematica']
        elif any(palabra in nombre_asignatura for palabra in ['fisica']):
            guias_template = guias_templates['fisica']
        elif any(palabra in nombre_asignatura for palabra in ['quimica']):
            guias_template = guias_templates['quimica']
        elif any(palabra in nombre_asignatura for palabra in ['programacion', 'algoritmos']):
            guias_template = guias_templates['programacion']
        else:
            guias_template = guias_templates['default']
        
        # Crear solo 1-2 guías por unidad temática (no más)
        for i, guia_data in enumerate(guias_template[:2]):  # Máximo 2 guías
            guia, created = GuiaLaboratorio.objects.get_or_create(
                unidad_tematica=unidad,
                numero=i + 1,
                defaults={
                    'nombre': guia_data['nombre'],
                    'descripcion': guia_data['descripcion']
                }
            )
            
            if created:
                total_guias_creadas += 1
                
                # Crear 2-3 prácticas por guía (cantidad razonable)
                for j, practica_data in enumerate(practicas_templates[:3]):
                    practica, practica_created = Practica.objects.get_or_create(
                        guia_laboratorio=guia,
                        numero=j + 1,
                        defaults={
                            'nombre': practica_data['nombre'],
                            'descripcion': practica_data['descripcion']
                        }
                    )
                    
                    if practica_created:
                        total_practicas_creadas += 1
    
    print(f"\n=== RESUMEN FINAL ===")
    print(f"✅ Guías de laboratorio creadas: {total_guias_creadas}")
    print(f"✅ Prácticas creadas: {total_practicas_creadas}")
    print(f"✅ Total guías en BD: {GuiaLaboratorio.objects.count()}")
    print(f"✅ Total prácticas en BD: {Practica.objects.count()}")
    
    # Verificación específica
    print(f"\n=== VERIFICACIÓN ===")
    unidad_economia = UnidadTematica.objects.filter(
        asignatura__nombre='economia_ingenieria'
    ).first()
    
    if unidad_economia:
        guias = GuiaLaboratorio.objects.filter(unidad_tematica=unidad_economia)
        print(f"Unidad 'Microeconomía': {guias.count()} guías")
        for guia in guias:
            practicas = Practica.objects.filter(guia_laboratorio=guia)
            print(f"  - {guia.nombre}: {practicas.count()} prácticas")
    
    # Estadísticas finales
    promedio_guias = GuiaLaboratorio.objects.count() / max(1, unidades_seleccionadas.count())
    promedio_practicas = Practica.objects.count() / max(1, GuiaLaboratorio.objects.count())
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   Promedio guías por unidad: {promedio_guias:.1f}")
    print(f"   Promedio prácticas por guía: {promedio_practicas:.1f}")

if __name__ == "__main__":
    crear_guias_y_practicas_inteligente()
