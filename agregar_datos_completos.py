#!/usr/bin/env python3
"""
Script para agregar datos de ejemplo completos para el sistema de guías de laboratorio
Incluye carreras y asignaturas
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
    print("🚀 Agregando datos de ejemplo completos para guías de laboratorio...")
    
    # Datos de carreras con sus asignaturas
    carreras_data = {
        "Ingeniería de Sistemas": {
            1: ["Introducción a la Programación", "Matemática Básica", "Física I"],
            2: ["Programación Estructurada", "Cálculo I", "Álgebra Lineal"],
            3: ["Programación Orientada a Objetos", "Estructura de Datos", "Bases de Datos I"],
            4: ["Arquitectura de Computadoras", "Redes de Computadoras I", "Ingeniería de Software I"],
            5: ["Sistemas Operativos", "Bases de Datos II", "Desarrollo Web"],
            6: ["Inteligencia Artificial", "Seguridad Informática", "Gestión de Proyectos"],
            7: ["Sistemas Distribuidos", "Minería de Datos", "Taller de Grado I"],
            8: ["Auditoría de Sistemas", "Computación Móvil", "Taller de Grado II"]
        },
        "Ingeniería Industrial": {
            1: ["Introducción a la Ingeniería", "Matemática Básica", "Física I"],
            2: ["Probabilidad y Estadística", "Cálculo I", "Química General"],
            3: ["Investigación Operativa I", "Termodinámica", "Mecánica de Fluidos"],
            4: ["Control de Calidad", "Diseño de Plantas", "Ergonomía"],
            5: ["Gestión de Operaciones", "Logística", "Seguridad Industrial"],
            6: ["Evaluación de Proyectos", "Gestión Ambiental", "Automatización"],
            7: ["Simulación de Sistemas", "Lean Manufacturing", "Taller de Grado I"],
            8: ["Auditoría Industrial", "Emprendimiento", "Taller de Grado II"]
        },
        "Ingeniería Civil": {
            1: ["Dibujo Técnico", "Matemática Básica", "Física I"],
            2: ["Topografía I", "Cálculo I", "Geología"],
            3: ["Mecánica de Suelos I", "Hidráulica I", "Resistencia de Materiales I"],
            4: ["Hormigón Armado I", "Estructuras Metálicas I", "Caminos I"],
            5: ["Hormigón Armado II", "Hidrología", "Construcciones I"],
            6: ["Puentes", "Abastecimiento de Agua", "Construcciones II"],
            7: ["Diseño Sísmico", "Alcantarillado", "Taller de Grado I"],
            8: ["Gestión de Construcción", "Impacto Ambiental", "Taller de Grado II"]
        },
        "Ingeniería Electrónica": {
            1: ["Circuitos Eléctricos I", "Matemática Básica", "Física I"],
            2: ["Circuitos Eléctricos II", "Cálculo I", "Programación Básica"],
            3: ["Electrónica Analógica I", "Señales y Sistemas", "Electromagnetismo"],
            4: ["Electrónica Digital I", "Microcontroladores", "Comunicaciones I"],
            5: ["Procesamiento Digital", "Control Automático", "Telecomunicaciones"],
            6: ["Instrumentación", "Sistemas Embebidos", "Antenas"],
            7: ["Robótica", "Sistemas de Comunicación", "Taller de Grado I"],
            8: ["Domótica", "Bioingeniería", "Taller de Grado II"]
        },
        "Ingeniería Mecánica": {
            1: ["Dibujo Técnico", "Matemática Básica", "Física I"],
            2: ["Mecánica Técnica I", "Cálculo I", "Química General"],
            3: ["Resistencia de Materiales", "Termodinámica I", "Mecánica de Fluidos I"],
            4: ["Máquinas Térmicas", "Diseño de Elementos", "Manufactura I"],
            5: ["Transferencia de Calor", "Vibraciones Mecánicas", "Manufactura II"],
            6: ["Refrigeración", "Mantenimiento Industrial", "Automatización"],
            7: ["Energías Renovables", "Control de Calidad", "Taller de Grado I"],
            8: ["Gestión de Mantenimiento", "Innovación Tecnológica", "Taller de Grado II"]
        },
        "Ingeniería Química": {
            1: ["Química General", "Matemática Básica", "Física I"],
            2: ["Química Orgánica", "Cálculo I", "Fisicoquímica I"],
            3: ["Balance de Materia", "Operaciones Unitarias I", "Fisicoquímica II"],
            4: ["Transferencia de Calor", "Operaciones Unitarias II", "Reactores Químicos I"],
            5: ["Ingeniería de Procesos", "Control de Procesos", "Biotecnología"],
            6: ["Diseño de Plantas", "Seguridad Industrial", "Análisis Instrumental"],
            7: ["Evaluación de Proyectos", "Gestión Ambiental", "Taller de Grado I"],
            8: ["Optimización de Procesos", "Emprendimiento", "Taller de Grado II"]
        },
        "Ingeniería Petrolera": {
            1: ["Geología General", "Matemática Básica", "Física I"],
            2: ["Geología del Petróleo", "Cálculo I", "Química General"],
            3: ["Petrofísica", "Mecánica de Fluidos", "Termodinámica"],
            4: ["Perforación I", "Producción I", "Evaluación de Formaciones"],
            5: ["Perforación II", "Producción II", "Simulación de Yacimientos"],
            6: ["Recuperación Mejorada", "Economía Petrolera", "Refinación"],
            7: ["Gestión de Yacimientos", "Impacto Ambiental", "Taller de Grado I"],
            8: ["Nuevas Tecnologías", "Emprendimiento", "Taller de Grado II"]
        },
        "Ingeniería en Biotecnología": {
            1: ["Biología General", "Matemática Básica", "Química General"],
            2: ["Bioquímica I", "Cálculo I", "Microbiología General"],
            3: ["Biología Molecular", "Bioestadística", "Microbiología Industrial"],
            4: ["Ingeniería Genética", "Bioingeniería", "Fermentaciones"],
            5: ["Biotecnología Vegetal", "Bioseparaciones", "Control de Calidad"],
            6: ["Biotecnología Animal", "Bioprocesos", "Regulación Biotecnológica"],
            7: ["Biotecnología Ambiental", "Bioseguridad", "Taller de Grado I"],
            8: ["Emprendimiento Biotecnológico", "Bioética", "Taller de Grado II"]
        }
    }
    
    carreras_creadas = 0
    asignaturas_creadas = 0
    
    for nombre_carrera, semestres in carreras_data.items():
        # Crear o obtener la carrera
        carrera, created = Carrera.objects.get_or_create(
            nombre=nombre_carrera,
            defaults={
                'codigo': nombre_carrera[:3].upper() + str(len(Carrera.objects.all()) + 1).zfill(3),
                'descripcion': f'Carrera de {nombre_carrera}',
                'duracion_semestres': 8,
                'modalidad': 'Presencial'
            }
        )
        
        if created:
            carreras_creadas += 1
            print(f"✅ Carrera creada: {nombre_carrera}")
        else:
            print(f"📋 Carrera existente: {nombre_carrera}")
        
        # Agregar asignaturas para cada semestre
        for semestre, asignaturas in semestres.items():
            for nombre_asignatura in asignaturas:
                asignatura, created = Asignatura.objects.get_or_create(
                    nombre=nombre_asignatura,
                    carrera=carrera,
                    semestre=semestre,
                    defaults={
                        'codigo': f"{carrera.codigo}{semestre}{len(asignaturas):02d}",
                        'creditos': 4,
                        'horas_teoricas': 3,
                        'horas_practicas': 2,
                        'prerequisitos': ""
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
        print(f"   - {carrera.nombre}: {total_asignaturas} asignaturas")

if __name__ == "__main__":
    main()
