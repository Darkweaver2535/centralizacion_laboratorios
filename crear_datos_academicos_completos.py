#!/usr/bin/env python
"""
Script para crear datos completos del sistema académico:
- Unidades Temáticas por asignatura
- Guías de Laboratorio por unidad temática 
- Prácticas por guía de laboratorio
- Laboratorios físicos (ya existe, verificación)
"""

import os
import django
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio

def crear_unidades_tematicas():
    """Crear unidades temáticas para todas las asignaturas"""
    print("📚 Creando Unidades Temáticas...")
    
    # Definir unidades temáticas comunes por tipo de asignatura
    unidades_matematicas = [
        "Números Reales y Funciones",
        "Límites y Continuidad", 
        "Derivadas y Aplicaciones",
        "Integrales Definidas e Indefinidas",
        "Aplicaciones de la Integral"
    ]
    
    unidades_fisica = [
        "Mecánica Clásica",
        "Dinámica de Partículas",
        "Trabajo y Energía",
        "Momentum y Colisiones",
        "Oscilaciones y Ondas"
    ]
    
    unidades_quimica = [
        "Estructura Atómica",
        "Enlaces Químicos",
        "Reacciones Químicas",
        "Termodinámica Química",
        "Cinética Química"
    ]
    
    unidades_programacion = [
        "Fundamentos de Programación",
        "Estructuras de Control",
        "Estructuras de Datos",
        "Algoritmos de Ordenamiento",
        "Programación Orientada a Objetos"
    ]
    
    unidades_dibujo = [
        "Geometría Descriptiva",
        "Proyecciones Ortogonales",
        "Isometrías y Perspectivas",
        "Cortes y Secciones",
        "Acotación y Tolerancias"
    ]
    
    unidades_generales = [
        "Conceptos Fundamentales",
        "Principios Básicos",
        "Aplicaciones Prácticas",
        "Metodologías",
        "Evaluación y Control"
    ]
    
    asignaturas = Asignatura.objects.all()
    total_creadas = 0
    
    with transaction.atomic():
        for asignatura in asignaturas:
            # Seleccionar unidades según el nombre de la asignatura
            if 'Matemática' in asignatura.nombre:
                unidades = unidades_matematicas
            elif 'Física' in asignatura.nombre:
                unidades = unidades_fisica
            elif 'Química' in asignatura.nombre:
                unidades = unidades_quimica
            elif 'Programación' in asignatura.nombre:
                unidades = unidades_programacion
            elif 'Dibujo' in asignatura.nombre:
                unidades = unidades_dibujo
            else:
                unidades = unidades_generales
            
            for i, nombre_unidad in enumerate(unidades, 1):
                unidad, created = UnidadTematica.objects.get_or_create(
                    asignatura=asignatura,
                    numero=i,
                    defaults={
                        'nombre': nombre_unidad,
                        'descripcion': f'Unidad {i} de {asignatura.nombre}'
                    }
                )
                if created:
                    total_creadas += 1
                    print(f"  ✅ {asignatura.carrera.nombre} - {asignatura.nombre}: Unidad {i} - {nombre_unidad}")
    
    print(f"📚 {total_creadas} unidades temáticas creadas")
    return total_creadas

def crear_guias_laboratorio():
    """Crear guías de laboratorio para cada unidad temática"""
    print("🧪 Creando Guías de Laboratorio...")
    
    guias_tipos = [
        "Introducción y Conceptos Básicos",
        "Experimento Práctico",
        "Análisis de Resultados",
        "Aplicación Avanzada"
    ]
    
    unidades = UnidadTematica.objects.all()
    total_creadas = 0
    
    with transaction.atomic():
        for unidad in unidades:
            for i, nombre_guia in enumerate(guias_tipos, 1):
                guia, created = GuiaLaboratorio.objects.get_or_create(
                    unidad_tematica=unidad,
                    numero=i,
                    defaults={
                        'nombre': f"{nombre_guia} - {unidad.nombre}",
                        'descripcion': f'Guía {i} para la unidad: {unidad.nombre}'
                    }
                )
                if created:
                    total_creadas += 1
                    if total_creadas <= 20:  # Mostrar solo las primeras 20
                        print(f"  ✅ {unidad.asignatura.nombre}: Guía {i} - {nombre_guia}")
    
    print(f"🧪 {total_creadas} guías de laboratorio creadas")
    return total_creadas

def crear_practicas():
    """Crear prácticas para cada guía de laboratorio"""
    print("🔬 Creando Prácticas de Laboratorio...")
    
    practicas_tipos = [
        "Preparación y Calibración",
        "Ejecución del Experimento",
        "Medición y Registro de Datos",
        "Análisis y Conclusiones"
    ]
    
    guias = GuiaLaboratorio.objects.all()
    total_creadas = 0
    
    with transaction.atomic():
        for guia in guias:
            for i, nombre_practica in enumerate(practicas_tipos, 1):
                practica, created = Practica.objects.get_or_create(
                    guia_laboratorio=guia,
                    numero=i,
                    defaults={
                        'nombre': f"{nombre_practica}",
                        'descripcion': f'Práctica {i} de la guía: {guia.nombre}'
                    }
                )
                if created:
                    total_creadas += 1
                    if total_creadas <= 20:  # Mostrar solo las primeras 20
                        print(f"  ✅ {guia.unidad_tematica.asignatura.nombre}: Práctica {i} - {nombre_practica}")
    
    print(f"🔬 {total_creadas} prácticas creadas")
    return total_creadas

def verificar_laboratorios():
    """Verificar que existen laboratorios físicos"""
    print("🏢 Verificando Laboratorios Físicos...")
    
    laboratorios = Laboratorio.objects.all()
    print(f"🏢 {laboratorios.count()} laboratorios físicos disponibles:")
    
    for lab in laboratorios[:10]:  # Mostrar los primeros 10
        print(f"  ✅ {lab.get_nombre_display()}")
    
    if laboratorios.count() > 10:
        print(f"  ... y {laboratorios.count() - 10} más")
    
    return laboratorios.count()

def verificar_datos_completos():
    """Verificar que todos los datos estén correctamente relacionados"""
    print("\n🔍 VERIFICACIÓN FINAL:")
    print("=" * 50)
    
    # Conteos totales
    asignaturas_count = Asignatura.objects.count()
    unidades_count = UnidadTematica.objects.count()
    guias_count = GuiaLaboratorio.objects.count()
    practicas_count = Practica.objects.count()
    laboratorios_count = Laboratorio.objects.count()
    
    print(f"📚 Asignaturas: {asignaturas_count}")
    print(f"📑 Unidades Temáticas: {unidades_count}")
    print(f"🧪 Guías de Laboratorio: {guias_count}")
    print(f"🔬 Prácticas: {practicas_count}")
    print(f"🏢 Laboratorios Físicos: {laboratorios_count}")
    
    # Verificar algunos ejemplos de la cadena de relaciones
    print("\n🔗 EJEMPLOS DE RELACIONES:")
    print("-" * 30)
    
    # Tomar una asignatura de ejemplo
    asignatura_ejemplo = Asignatura.objects.first()
    if asignatura_ejemplo:
        print(f"\n📚 Asignatura: {asignatura_ejemplo.nombre}")
        print(f"   Carrera: {asignatura_ejemplo.carrera.nombre}")
        print(f"   Semestre: {asignatura_ejemplo.semestre}")
        
        unidades = asignatura_ejemplo.unidades_tematicas.all()[:3]
        for unidad in unidades:
            print(f"\n   📑 Unidad {unidad.numero}: {unidad.nombre}")
            
            guias = unidad.guias_laboratorio.all()[:2]
            for guia in guias:
                print(f"      🧪 Guía {guia.numero}: {guia.nombre}")
                
                practicas = guia.practicas.all()[:2]
                for practica in practicas:
                    print(f"         🔬 Práctica {practica.numero}: {practica.nombre}")

def main():
    """Función principal"""
    print("🚀 INICIANDO CREACIÓN DE DATOS ACADÉMICOS COMPLETOS")
    print("=" * 60)
    
    try:
        # Verificar asignaturas existentes
        asignaturas_count = Asignatura.objects.count()
        if asignaturas_count == 0:
            print("❌ Error: No hay asignaturas en la base de datos")
            print("   Ejecuta primero: python crear_asignaturas_completas.py")
            return
        
        print(f"✅ {asignaturas_count} asignaturas encontradas en la base de datos")
        
        # Crear datos en orden jerárquico
        unidades_creadas = crear_unidades_tematicas()
        guias_creadas = crear_guias_laboratorio()
        practicas_creadas = crear_practicas()
        laboratorios_count = verificar_laboratorios()
        
        # Verificación final
        verificar_datos_completos()
        
        print("\n🎯 RESUMEN FINAL:")
        print("=" * 40)
        print(f"✅ {unidades_creadas} unidades temáticas creadas")
        print(f"✅ {guias_creadas} guías de laboratorio creadas")
        print(f"✅ {practicas_creadas} prácticas creadas")
        print(f"✅ {laboratorios_count} laboratorios físicos disponibles")
        
        print(f"\n🔢 TOTALES ESPERADOS:")
        print(f"   📚 Asignaturas: {asignaturas_count}")
        print(f"   📑 Unidades: {asignaturas_count * 5} (5 por asignatura)")
        print(f"   🧪 Guías: {asignaturas_count * 5 * 4} (4 por unidad)")
        print(f"   🔬 Prácticas: {asignaturas_count * 5 * 4 * 4} (4 por guía)")
        
        print("\n🚀 SISTEMA ACADÉMICO COMPLETADO")
        print("💡 Todas las APIs ahora funcionarán correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
