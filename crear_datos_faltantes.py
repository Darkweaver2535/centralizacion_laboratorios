#!/usr/bin/env python3
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    Asignatura, UnidadTematica, GuiaLaboratorio, 
    Practica, Laboratorio, Carrera, UnidadAcademica
)

def crear_datos_faltantes():
    print("=== CREANDO DATOS FALTANTES ===")
    
    # Obtener algunas carreras para asociar
    carreras = list(Carrera.objects.all()[:5])
    unidades = list(UnidadAcademica.objects.all())
    
    if not carreras:
        print("ERROR: No hay carreras en la BD")
        return
    
    # 1. CREAR LABORATORIOS (10 ejemplos)
    print("\n1. Creando Laboratorios...")
    laboratorios_data = [
        {'nombre': 'Laboratorio de Química General', 'codigo': 'LAB-QUI-001', 'capacidad': 25, 'ubicacion': 'Edificio A - Piso 2'},
        {'nombre': 'Laboratorio de Física Básica', 'codigo': 'LAB-FIS-001', 'capacidad': 30, 'ubicacion': 'Edificio B - Piso 1'},
        {'nombre': 'Laboratorio de Biología', 'codigo': 'LAB-BIO-001', 'capacidad': 20, 'ubicacion': 'Edificio C - Piso 3'},
        {'nombre': 'Laboratorio de Sistemas Digitales', 'codigo': 'LAB-SIS-001', 'capacidad': 35, 'ubicacion': 'Edificio D - Piso 2'},
        {'nombre': 'Laboratorio de Materiales', 'codigo': 'LAB-MAT-001', 'capacidad': 15, 'ubicacion': 'Edificio E - Piso 1'},
        {'nombre': 'Laboratorio de Electrónica', 'codigo': 'LAB-ELE-001', 'capacidad': 28, 'ubicacion': 'Edificio F - Piso 2'},
        {'nombre': 'Laboratorio de Mecánica', 'codigo': 'LAB-MEC-001', 'capacidad': 22, 'ubicacion': 'Taller - Piso 1'},
        {'nombre': 'Laboratorio de Computación', 'codigo': 'LAB-COM-001', 'capacidad': 40, 'ubicacion': 'Edificio G - Piso 3'},
        {'nombre': 'Laboratorio de Química Orgánica', 'codigo': 'LAB-QUI-002', 'capacidad': 18, 'ubicacion': 'Edificio A - Piso 3'},
        {'nombre': 'Laboratorio de Termodinámica', 'codigo': 'LAB-TER-001', 'capacidad': 26, 'ubicacion': 'Edificio H - Piso 1'}
    ]
    
    laboratorios_creados = []
    for lab_data in laboratorios_data:
        laboratorio, created = Laboratorio.objects.get_or_create(
            identificador_aula=lab_data['codigo'],
            defaults={
                'nombre': lab_data['nombre'],
                'capacidad': lab_data['capacidad'],
                'ubicacion': lab_data['ubicacion'],
                'descripcion': f"Laboratorio especializado para {lab_data['nombre'].lower()}",
                'responsable': 'Por asignar',
                'seccion_area': 'Laboratorios Académicos'
            }
        )
        laboratorios_creados.append(laboratorio)
        if created:
            print(f"✓ Creado: {laboratorio.nombre}")
    
    # 2. CREAR ASIGNATURAS (10 ejemplos)
    print("\n2. Creando Asignaturas...")
    asignaturas_data = [
        {'nombre': 'Química General I', 'semestre': 1, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Física I', 'semestre': 1, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Matemática I', 'semestre': 1, 'carga_semanal': 5, 'carga_semestral': 80},
        {'nombre': 'Programación I', 'semestre': 2, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Biología General', 'semestre': 2, 'carga_semanal': 3, 'carga_semestral': 48},
        {'nombre': 'Termodinámica', 'semestre': 3, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Electrónica Básica', 'semestre': 3, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Mecánica de Fluidos', 'semestre': 4, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Sistemas Digitales', 'semestre': 4, 'carga_semanal': 4, 'carga_semestral': 64},
        {'nombre': 'Química Orgánica', 'semestre': 4, 'carga_semanal': 3, 'carga_semestral': 48}
    ]
    
    asignaturas_creadas = []
    for asig_data in asignaturas_data:
        asignatura, created = Asignatura.objects.get_or_create(
            nombre=asig_data['nombre'],
            carrera=carreras[0],
            defaults={
                'semestre': asig_data['semestre'],
                'carga_horaria_semanal': asig_data['carga_semanal'],
                'carga_horaria_semestral': asig_data['carga_semestral']
            }
        )
        asignaturas_creadas.append(asignatura)
        if created:
            print(f"✓ Creado: {asignatura.nombre}")
    
    # 3. CREAR UNIDADES TEMÁTICAS (10 ejemplos)
    print("\n3. Creando Unidades Temáticas...")
    unidades_tematicas_data = [
        {'nombre': 'Estructura Atómica', 'descripcion': 'Fundamentos de la estructura del átomo', 'numero': 1},
        {'nombre': 'Enlaces Químicos', 'descripcion': 'Tipos de enlaces y propiedades', 'numero': 2},
        {'nombre': 'Cinemática', 'descripcion': 'Movimiento en una y dos dimensiones', 'numero': 1},
        {'nombre': 'Dinámica', 'descripcion': 'Fuerzas y leyes de Newton', 'numero': 2},
        {'nombre': 'Algoritmos Básicos', 'descripcion': 'Fundamentos de programación', 'numero': 1},
        {'nombre': 'Estructuras de Control', 'descripcion': 'Condicionales y bucles', 'numero': 2},
        {'nombre': 'Célula Eucariota', 'descripcion': 'Estructura y función celular', 'numero': 1},
        {'nombre': 'División Celular', 'descripcion': 'Mitosis y meiosis', 'numero': 2},
        {'nombre': 'Primer Principio', 'descripcion': 'Conservación de la energía', 'numero': 1},
        {'nombre': 'Segundo Principio', 'descripcion': 'Entropía y procesos irreversibles', 'numero': 2}
    ]
    
    unidades_creadas = []
    for i, unidad_data in enumerate(unidades_tematicas_data):
        asignatura = asignaturas_creadas[i % len(asignaturas_creadas)]
        unidad, created = UnidadTematica.objects.get_or_create(
            nombre=unidad_data['nombre'],
            asignatura=asignatura,
            defaults={
                'descripcion': unidad_data['descripcion'],
                'numero': unidad_data['numero']
            }
        )
        unidades_creadas.append(unidad)
        if created:
            print(f"✓ Creado: {unidad.nombre} - {asignatura.nombre}")
    
    # 4. CREAR GUÍAS DE LABORATORIO (10 ejemplos)
    print("\n4. Creando Guías de Laboratorio...")
    guias_data = [
        {'nombre': 'Identificación de Elementos Químicos', 'descripcion': 'Técnicas de identificación mediante reacciones'},
        {'nombre': 'Medición de Velocidad', 'descripcion': 'Experimentos de cinemática básica'},
        {'nombre': 'Preparación de Soluciones', 'descripcion': 'Cálculos de concentración y dilución'},
        {'nombre': 'Ley de Ohm', 'descripcion': 'Verificación experimental de la ley de Ohm'},
        {'nombre': 'Observación Microscópica', 'descripcion': 'Técnicas de preparación de muestras'},
        {'nombre': 'Programación Básica', 'descripcion': 'Ejercicios fundamentales de programación'},
        {'nombre': 'Análisis de Circuitos', 'descripcion': 'Medición de corriente y voltaje'},
        {'nombre': 'Propiedades de los Materiales', 'descripcion': 'Ensayos de dureza y resistencia'},
        {'nombre': 'Intercambiadores de Calor', 'descripcion': 'Análisis de transferencia de calor'},
        {'nombre': 'Síntesis Orgánica', 'descripcion': 'Preparación de compuestos orgánicos simples'}
    ]
    
    guias_creadas = []
    for i, guia_data in enumerate(guias_data):
        unidad = unidades_creadas[i % len(unidades_creadas)]
        
        guia, created = GuiaLaboratorio.objects.get_or_create(
            nombre=guia_data['nombre'],
            unidad_tematica=unidad,
            defaults={
                'descripcion': guia_data['descripcion'],
                'numero': (i % 3) + 1
            }
        )
        guias_creadas.append(guia)
        if created:
            print(f"✓ Creado: {guia.nombre}")
    
    # 5. CREAR PRÁCTICAS (10 ejemplos)
    print("\n5. Creando Prácticas...")
    practicas_data = [
        {'nombre': 'Práctica 1 - Reacciones Químicas', 'descripcion': 'Observación de diferentes tipos de reacciones'},
        {'nombre': 'Práctica 2 - Movimiento Rectilíneo', 'descripcion': 'Análisis del movimiento uniforme'},
        {'nombre': 'Práctica 3 - Concentraciones', 'descripcion': 'Preparación de soluciones estándar'},
        {'nombre': 'Práctica 4 - Circuitos DC', 'descripcion': 'Análisis de circuitos de corriente continua'},
        {'nombre': 'Práctica 5 - Células Vegetales', 'descripcion': 'Observación de estructuras celulares'},
        {'nombre': 'Práctica 6 - Algoritmos de Ordenamiento', 'descripcion': 'Implementación de algoritmos básicos'},
        {'nombre': 'Práctica 7 - Amplificadores', 'descripcion': 'Diseño y análisis de amplificadores'},
        {'nombre': 'Práctica 8 - Ensayos Mecánicos', 'descripcion': 'Pruebas de tracción y compresión'},
        {'nombre': 'Práctica 9 - Ciclos Termodinámicos', 'descripcion': 'Análisis de ciclos de potencia'},
        {'nombre': 'Práctica 10 - Reacciones de Síntesis', 'descripcion': 'Preparación de compuestos orgánicos'}
    ]
    
    for i, practica_data in enumerate(practicas_data):
        guia = guias_creadas[i % len(guias_creadas)]
        
        practica, created = Practica.objects.get_or_create(
            nombre=practica_data['nombre'],
            guia_laboratorio=guia,
            defaults={
                'descripcion': practica_data['descripcion'],
                'numero': (i % 3) + 1
            }
        )
        if created:
            print(f"✓ Creado: {practica.nombre}")
    
    print("\n=== RESUMEN FINAL ===")
    print(f"Laboratorios: {Laboratorio.objects.count()}")
    print(f"Asignaturas: {Asignatura.objects.count()}")
    print(f"Unidades Temáticas: {UnidadTematica.objects.count()}")
    print(f"Guías de Laboratorio: {GuiaLaboratorio.objects.count()}")
    print(f"Prácticas: {Practica.objects.count()}")
    print("\n¡Datos creados exitosamente!")

if __name__ == "__main__":
    crear_datos_faltantes()
