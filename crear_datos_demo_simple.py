#!/usr/bin/env python
"""
Script simplificado para crear datos de demostración
"""
import os
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio
from equipos.models import Equipo

def crear_datos_demo():
    """Crear datos de demo simplificados"""
    print("🧹 Limpiando equipos existentes...")
    Equipo.objects.all().delete()
    
    print("🔄 Creando datos de demostración...")
    
    # Obtener objetos base
    try:
        unidades = list(UnidadAcademica.objects.all())
        carreras = list(Carrera.objects.all())
        
        # Crear un laboratorio básico si no existe
        laboratorio, _ = Laboratorio.objects.get_or_create(
            nombre="Laboratorio Demo",
            defaults={
                'descripcion': 'Laboratorio para demostración',
                'capacidad': 20,
                'ubicacion': 'Edificio Principal'
            }
        )
        
        print(f"Unidades disponibles: {len(unidades)}")
        print(f"Carreras disponibles: {len(carreras)}")
        
    except Exception as e:
        print(f"Error obteniendo datos base: {e}")
        return
    
    # Crear algunos equipos de demostración
    equipos_demo = [
        "Microscopio Óptico",
        "Balanza Analítica", 
        "Computadora de Escritorio",
        "Multímetro Digital",
        "Osciloscopio",
        "Fuente de Poder",
        "Generador de Funciones",
        "Espectrofotómetro",
        "Centrífuga",
        "Autoclave",
        "pH-metro",
        "Agitador Magnético",
        "Horno de Laboratorio",
        "Refrigeradora",
        "Proyector",
        "Impresora 3D",
        "Soldadora",
        "Taladro de Banco",
        "Sierra Circular",
        "Torno"
    ]
    
    equipos_creados = 0
    
    # Crear múltiples equipos para demostración
    for i in range(200):  # Crear 200 equipos
        try:
            # Seleccionar datos aleatorios
            unidad = unidades[i % len(unidades)]
            carrera = carreras[i % len(carreras)]
            nombre_equipo = equipos_demo[i % len(equipos_demo)]
            
            # Crear asignatura si no existe
            asignatura, _ = Asignatura.objects.get_or_create(
                nombre=f"asignatura_demo_{i % 10}",
                defaults={'carrera': carrera}
            )
            
            # Crear el equipo con solo los campos obligatorios
            equipo = Equipo.objects.create(
                # Campos obligatorios
                unidad_academica=unidad,
                carrera=carrera,
                asignatura=asignatura,
                laboratorio=laboratorio,
                equipo_existente=f"{nombre_equipo} {i+1}",
                
                # Campos básicos con datos demo
                semestre=((i % 8) + 1),  # Semestres 1-8
                carga_horaria_semestral=(i % 4 + 2) * 20,  # 40, 60, 80, 100
                carga_horaria_semanal=(i % 4) + 2,  # 2, 3, 4, 5
                
                # Campos por defecto
                estado='bueno',
                numero_unidades=1,
                es_activo_fijo=False,
                marca="",
                modelo="",
                seccion_area="",
                identificador_aula=""
            )
            
            equipos_creados += 1
            
            if equipos_creados % 50 == 0:
                print(f"✅ Creados {equipos_creados} equipos...")
                
        except Exception as e:
            print(f"❌ Error creando equipo {i+1}: {e}")
            continue
    
    print(f"\n🎉 Demostración creada exitosamente!")
    print(f"   ✅ Equipos creados: {equipos_creados}")
    print(f"   📊 Total en BD: {Equipo.objects.count()}")
    
    # Mostrar ejemplos
    if Equipo.objects.exists():
        primer_equipo = Equipo.objects.first()
        print(f"\n🔍 EJEMPLO DE EQUIPO:")
        print(f"   • ID: {primer_equipo.id}")
        print(f"   • Nombre: {primer_equipo.equipo_existente}")
        print(f"   • Unidad: {primer_equipo.unidad_academica.get_nombre_display()}")
        print(f"   • Carrera: {primer_equipo.carrera.get_nombre_display()}")
        print(f"   • Semestre: {primer_equipo.semestre}")

if __name__ == '__main__':
    print("🚀 Iniciando creación de datos de demostración")
    print("="*50)
    crear_datos_demo()
    print("\n✅ ¡Listo para la demostración!")
