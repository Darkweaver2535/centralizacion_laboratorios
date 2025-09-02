#!/usr/bin/env python
"""
Script para limpiar datos de equipos para demostración.
Mantiene solo los campos básicos de malla curricular:
1. UNIDAD ACADÉMICA 
2. CARRERA 
3. SEMESTRE 
4. ASIGNATURA 
5. CARGA HORARIA SEMESTRAL 
6. CARGA HORARIA SEMANAL 
7. CRITERIO DE DESEMPEÑO 
8. UNIDAD DIDACTICA 
9. CONTENIDO ANALITICO

Limpia todos los campos posteriores para que el usuario pueda demostrar
la funcionalidad de edición.
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import GuiaLaboratorio, Practica, Laboratorio
from django.db import transaction

def crear_valores_demo():
    """
    Crea valores por defecto para la demostración.
    """
    print("🔧 Creando valores por defecto para demostración...")
    
    # Obtener la primera unidad temática existente o crear una nueva
    from core.models import UnidadTematica, Asignatura
    
    unidad_tematica = UnidadTematica.objects.first()
    if not unidad_tematica:
        # Crear una unidad temática básica si no existe
        asignatura = Asignatura.objects.first()
        if asignatura:
            unidad_tematica = UnidadTematica.objects.create(
                asignatura=asignatura,
                nombre="Unidad por completar",
                numero=999,
                descripcion="Esta unidad debe ser completada por el usuario."
            )
            print("✅ Unidad temática por defecto creada")
    
    # Crear o obtener guía por defecto
    guia_demo, created = GuiaLaboratorio.objects.get_or_create(
        numero=999,
        unidad_tematica=unidad_tematica,
        defaults={
            'nombre': 'Guía por completar',
            'descripcion': 'Esta guía debe ser completada por el usuario usando la funcionalidad de edición.'
        }
    )
    if created:
        print("✅ Guía por defecto creada")
    
    # Crear o obtener práctica por defecto
    practica_demo, created = Practica.objects.get_or_create(
        numero=999,
        guia_laboratorio=guia_demo,
        defaults={
            'nombre': 'Práctica por completar',
            'descripcion': 'Esta práctica debe ser completada por el usuario usando la funcionalidad de edición.'
        }
    )
    if created:
        print("✅ Práctica por defecto creada")
    
    # Crear o obtener laboratorio por defecto
    laboratorio_demo, created = Laboratorio.objects.get_or_create(
        nombre="LAB_POR_ASIGNAR",
        defaults={
            'descripcion': 'Este laboratorio debe ser asignado por el usuario usando la funcionalidad de edición.',
            'seccion_area': '',
            'identificador_aula': ''
        }
    )
    if created:
        print("✅ Laboratorio por defecto creado")
    
    return guia_demo, practica_demo, laboratorio_demo

def limpiar_datos_demo():
    """
    Limpia los datos de equipos manteniendo solo la malla curricular básica.
    """
    print("🧹 Iniciando limpieza de datos para demostración...")
    
    # Crear valores por defecto
    guia_demo, practica_demo, laboratorio_demo = crear_valores_demo()
    
    equipos = Equipo.objects.all()
    total_equipos = equipos.count()
    
    print(f"📊 Total de equipos a procesar: {total_equipos}")
    
    with transaction.atomic():
        equipos_actualizados = 0
        
        for equipo in equipos:
            # Solo limpiamos si el equipo tiene datos de malla curricular completos
            if (equipo.unidad_academica and equipo.carrera and equipo.semestre and 
                equipo.asignatura and equipo.carga_horaria_semanal and 
                equipo.carga_horaria_semestral):
                
                # Limpiar campos que van después de contenido_analítico
                # Usar valores por defecto para campos obligatorios
                equipo.guia_laboratorio = guia_demo
                equipo.practica = practica_demo
                equipo.laboratorio = laboratorio_demo
                
                # Limpiar campos opcionales
                equipo.equipo_existente = "Equipo por completar"
                equipo.marca = ""
                equipo.modelo = ""
                equipo.estado = "bueno"  # Valor por defecto
                equipo.numero_unidades_equipo = None
                equipo.es_activo_fijo = False
                equipo.fotografia_frontal = None
                equipo.fotografia_placa = None
                equipo.equipo_requerido = ""
                equipo.numero_equipos_requeridos = 0
                
                equipo.save()
                equipos_actualizados += 1
                
                if equipos_actualizados % 100 == 0:
                    print(f"✅ Procesados {equipos_actualizados} equipos...")
    
    print(f"🎯 Limpieza completada:")
    print(f"   - Equipos procesados: {equipos_actualizados}")
    print(f"   - Datos mantenidos: Malla curricular básica (9 campos)")
    print(f"   - Datos limpiados: Campos desde 'Guía de Laboratorio' en adelante")
    print(f"\n🚀 Los usuarios ahora podrán usar la funcionalidad de edición")
    print(f"   para completar los datos faltantes desde http://127.0.0.1:8000/visualizacion/")

def verificar_limpieza():
    """
    Verifica que la limpieza se realizó correctamente.
    """
    print("\n🔍 Verificando limpieza...")
    
    equipos_sample = Equipo.objects.all()[:5]
    
    for i, equipo in enumerate(equipos_sample, 1):
        print(f"\nEquipo {i} (ID: {equipo.id}):")
        print(f"  ✅ Unidad Académica: {equipo.unidad_academica}")
        print(f"  ✅ Carrera: {equipo.carrera}")
        print(f"  ✅ Semestre: {equipo.semestre}")
        print(f"  ✅ Asignatura: {equipo.asignatura}")
        print(f"  ✅ Carga Semanal: {equipo.carga_horaria_semanal}")
        print(f"  ✅ Carga Semestral: {equipo.carga_horaria_semestral}")
        print(f"  ✅ Criterio: {equipo.criterio_desempeno}")
        print(f"  ✅ Unidad Didáctica: {equipo.unidad_didactica}")
        print(f"  ✅ Contenido Analítico: {equipo.contenido_analitico}")
        print(f"  🧹 Guía: {equipo.guia_laboratorio.nombre} (demo)")
        print(f"  🧹 Práctica: {equipo.practica.nombre} (demo)")
        print(f"  🧹 Equipo Existente: '{equipo.equipo_existente}' (demo)")
        print(f"  🧹 Marca: '{equipo.marca}' (limpiado)")
        print(f"  🧹 Laboratorio: {equipo.laboratorio.nombre} (demo)")

if __name__ == "__main__":
    limpiar_datos_demo()
    verificar_limpieza()
    print("\n✨ ¡Demo lista! Los usuarios pueden ahora completar los datos usando la funcionalidad de edición.")
    print("🎯 Visite http://127.0.0.1:8000/visualizacion/ y use los botones 'Editar' para completar los datos.")
