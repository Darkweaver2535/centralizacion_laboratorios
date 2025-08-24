#!/usr/bin/env python3
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, UnidadTematica

def crear_unidades_tematicas():
    print("=== CREANDO UNIDADES TEMÁTICAS PARA TODAS LAS ASIGNATURAS ===")
    
    # Plantillas de unidades temáticas por tipo de asignatura
    unidades_por_materia = {
        # Matemáticas
        'matematica': [
            {'nombre': 'Números Reales', 'numero': 1, 'descripcion': 'Propiedades y operaciones con números reales'},
            {'nombre': 'Funciones', 'numero': 2, 'descripcion': 'Definición y tipos de funciones'},
            {'nombre': 'Límites', 'numero': 3, 'descripcion': 'Concepto y cálculo de límites'},
        ],
        'fisica': [
            {'nombre': 'Mecánica Clásica', 'numero': 1, 'descripcion': 'Cinemática y dinámica de partículas'},
            {'nombre': 'Energía y Trabajo', 'numero': 2, 'descripcion': 'Conceptos de energía cinética y potencial'},
            {'nombre': 'Conservación', 'numero': 3, 'descripcion': 'Leyes de conservación en física'},
        ],
        'quimica': [
            {'nombre': 'Estructura Atómica', 'numero': 1, 'descripcion': 'Modelo atómico moderno'},
            {'nombre': 'Enlaces Químicos', 'numero': 2, 'descripcion': 'Tipos de enlaces y propiedades'},
            {'nombre': 'Reacciones Químicas', 'numero': 3, 'descripcion': 'Balanceo y tipos de reacciones'},
        ],
        'ingenieria': [
            {'nombre': 'Fundamentos', 'numero': 1, 'descripcion': 'Principios básicos de la ingeniería'},
            {'nombre': 'Metodología', 'numero': 2, 'descripcion': 'Métodos de resolución de problemas'},
            {'nombre': 'Aplicaciones', 'numero': 3, 'descripcion': 'Casos prácticos y aplicaciones'},
        ],
        'programacion': [
            {'nombre': 'Algoritmos Básicos', 'numero': 1, 'descripcion': 'Estructuras algorítmicas fundamentales'},
            {'nombre': 'Estructuras de Control', 'numero': 2, 'descripcion': 'Condicionales y bucles'},
            {'nombre': 'Funciones y Procedimientos', 'numero': 3, 'descripcion': 'Modularización del código'},
        ],
        'economia': [
            {'nombre': 'Microeconomía', 'numero': 1, 'descripcion': 'Comportamiento de agentes económicos'},
            {'nombre': 'Macroeconomía', 'numero': 2, 'descripcion': 'Agregados económicos nacionales'},
            {'nombre': 'Finanzas', 'numero': 3, 'descripcion': 'Gestión financiera y análisis de inversiones'},
        ],
        'estadistica': [
            {'nombre': 'Estadística Descriptiva', 'numero': 1, 'descripcion': 'Medidas de tendencia central y dispersión'},
            {'nombre': 'Probabilidades', 'numero': 2, 'descripcion': 'Teoría de probabilidades y distribuciones'},
            {'nombre': 'Inferencia Estadística', 'numero': 3, 'descripcion': 'Estimación y pruebas de hipótesis'},
        ],
        'mecanica': [
            {'nombre': 'Estática', 'numero': 1, 'descripcion': 'Equilibrio de fuerzas y momentos'},
            {'nombre': 'Cinemática', 'numero': 2, 'descripcion': 'Descripción del movimiento'},
            {'nombre': 'Dinámica', 'numero': 3, 'descripcion': 'Relación entre fuerzas y movimiento'},
        ],
        'dibujo': [
            {'nombre': 'Proyecciones Ortogonales', 'numero': 1, 'descripcion': 'Vistas principales de objetos'},
            {'nombre': 'Perspectiva Isométrica', 'numero': 2, 'descripcion': 'Representación tridimensional'},
            {'nombre': 'Planos Técnicos', 'numero': 3, 'descripcion': 'Elaboración de planos de ingeniería'},
        ],
        'default': [
            {'nombre': 'Fundamentos Teóricos', 'numero': 1, 'descripcion': 'Conceptos básicos y fundamentales'},
            {'nombre': 'Desarrollo Práctico', 'numero': 2, 'descripcion': 'Aplicación práctica de conceptos'},
            {'nombre': 'Evaluación y Síntesis', 'numero': 3, 'descripcion': 'Integración y evaluación de conocimientos'},
        ]
    }
    
    # Obtener todas las asignaturas
    asignaturas = Asignatura.objects.all()
    total_asignaturas = asignaturas.count()
    
    print(f"Procesando {total_asignaturas} asignaturas...")
    
    total_unidades_creadas = 0
    asignaturas_procesadas = 0
    
    for asignatura in asignaturas:
        # Determinar qué plantilla usar basándose en el nombre de la asignatura
        nombre_lower = asignatura.nombre.lower()
        
        if 'matematica' in nombre_lower or 'calculo' in nombre_lower:
            plantilla = unidades_por_materia['matematica']
        elif 'fisica' in nombre_lower:
            plantilla = unidades_por_materia['fisica']
        elif 'quimica' in nombre_lower:
            plantilla = unidades_por_materia['quimica']
        elif 'programacion' in nombre_lower or 'algoritmos' in nombre_lower:
            plantilla = unidades_por_materia['programacion']
        elif 'economia' in nombre_lower or 'finanzas' in nombre_lower:
            plantilla = unidades_por_materia['economia']
        elif 'estadistica' in nombre_lower or 'probabilidad' in nombre_lower:
            plantilla = unidades_por_materia['estadistica']
        elif 'mecanica' in nombre_lower or 'dinamica' in nombre_lower:
            plantilla = unidades_por_materia['mecanica']
        elif 'dibujo' in nombre_lower:
            plantilla = unidades_por_materia['dibujo']
        elif 'ingenieria' in nombre_lower or 'introduccion' in nombre_lower:
            plantilla = unidades_por_materia['ingenieria']
        else:
            plantilla = unidades_por_materia['default']
        
        # Crear unidades temáticas para esta asignatura
        unidades_creadas_asig = 0
        for unidad_data in plantilla:
            unidad, created = UnidadTematica.objects.get_or_create(
                asignatura=asignatura,
                numero=unidad_data['numero'],
                defaults={
                    'nombre': unidad_data['nombre'],
                    'descripcion': unidad_data['descripcion']
                }
            )
            
            if created:
                unidades_creadas_asig += 1
                total_unidades_creadas += 1
        
        asignaturas_procesadas += 1
        
        # Mostrar progreso cada 100 asignaturas
        if asignaturas_procesadas % 100 == 0:
            print(f"Procesadas {asignaturas_procesadas}/{total_asignaturas} asignaturas...")
    
    print(f"\n=== RESUMEN FINAL ===")
    print(f"✅ Asignaturas procesadas: {asignaturas_procesadas}")
    print(f"✅ Unidades temáticas creadas: {total_unidades_creadas}")
    print(f"✅ Total unidades temáticas en BD: {UnidadTematica.objects.count()}")
    
    # Verificación específica
    print(f"\n=== VERIFICACIÓN ===")
    asignatura_test = Asignatura.objects.filter(nombre='economia_ingenieria').first()
    if asignatura_test:
        unidades_test = UnidadTematica.objects.filter(asignatura=asignatura_test)
        print(f"Asignatura 'economia_ingenieria': {unidades_test.count()} unidades temáticas")
        for unidad in unidades_test:
            print(f"  - {unidad.nombre}")

if __name__ == "__main__":
    crear_unidades_tematicas()
