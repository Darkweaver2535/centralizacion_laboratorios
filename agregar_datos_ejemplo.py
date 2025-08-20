#!/usr/bin/env python
"""
Script para agregar datos de ejemplo para el módulo de guías
Ejecutar con: python manage.py shell < agregar_datos_ejemplo.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from ingreso_datos.models import Carrera, Asignatura

def agregar_datos_ejemplo():
    print("🚀 Agregando datos de ejemplo para guías de laboratorio...")
    
    # Obtener todas las carreras existentes
    carreras = Carrera.objects.all()
    
    if not carreras.exists():
        print("❌ No se encontraron carreras. Primero agrega carreras a la base de datos.")
        return
    
    # Datos de asignaturas por carrera
    asignaturas_por_carrera = {
        'SISTEMAS': [
            {'nombre': 'Algoritmos y Estructuras de Datos', 'semestres': [3, 4]},
            {'nombre': 'Base de Datos', 'semestres': [4, 5]},
            {'nombre': 'Programación I', 'semestres': [1, 2]},
            {'nombre': 'Programación II', 'semestres': [2, 3]},
            {'nombre': 'Ingeniería de Software', 'semestres': [5, 6]},
            {'nombre': 'Redes de Computadoras', 'semestres': [6, 7]},
            {'nombre': 'Inteligencia Artificial', 'semestres': [7, 8]},
            {'nombre': 'Sistemas Operativos', 'semestres': [5, 6]},
            {'nombre': 'Desarrollo Web', 'semestres': [4, 5]},
            {'nombre': 'Seguridad Informática', 'semestres': [7, 8]},
        ],
        'CIVIL': [
            {'nombre': 'Resistencia de Materiales', 'semestres': [4, 5]},
            {'nombre': 'Mecánica de Suelos', 'semestres': [5, 6]},
            {'nombre': 'Hormigón Armado', 'semestres': [6, 7]},
            {'nombre': 'Hidráulica', 'semestres': [5, 6]},
            {'nombre': 'Topografía', 'semestres': [3, 4]},
            {'nombre': 'Geotecnia', 'semestres': [6, 7]},
            {'nombre': 'Estructuras de Acero', 'semestres': [7, 8]},
            {'nombre': 'Construcciones', 'semestres': [7, 8]},
            {'nombre': 'Física I', 'semestres': [1, 2]},
            {'nombre': 'Física II', 'semestres': [2, 3]},
        ],
        'INDUSTRIAL': [
            {'nombre': 'Procesos Industriales', 'semestres': [4, 5]},
            {'nombre': 'Control de Calidad', 'semestres': [5, 6]},
            {'nombre': 'Investigación de Operaciones', 'semestres': [5, 6]},
            {'nombre': 'Gestión de Producción', 'semestres': [6, 7]},
            {'nombre': 'Automatización Industrial', 'semestres': [7, 8]},
            {'nombre': 'Ergonomía', 'semestres': [6, 7]},
            {'nombre': 'Logística', 'semestres': [7, 8]},
            {'nombre': 'Estadística Industrial', 'semestres': [4, 5]},
            {'nombre': 'Física I', 'semestres': [1, 2]},
            {'nombre': 'Química General', 'semestres': [2, 3]},
        ],
        'ELECTRONICA': [
            {'nombre': 'Circuitos Eléctricos', 'semestres': [3, 4]},
            {'nombre': 'Electrónica Analógica', 'semestres': [4, 5]},
            {'nombre': 'Electrónica Digital', 'semestres': [5, 6]},
            {'nombre': 'Microcontroladores', 'semestres': [6, 7]},
            {'nombre': 'Telecomunicaciones', 'semestres': [7, 8]},
            {'nombre': 'Instrumentación', 'semestres': [5, 6]},
            {'nombre': 'Control Automático', 'semestres': [6, 7]},
            {'nombre': 'Procesamiento Digital de Señales', 'semestres': [7, 8]},
            {'nombre': 'Física I', 'semestres': [1, 2]},
            {'nombre': 'Matemáticas I', 'semestres': [1, 2]},
        ],
        'COMERCIAL': [
            {'nombre': 'Contabilidad General', 'semestres': [1, 2]},
            {'nombre': 'Administración de Empresas', 'semestres': [2, 3]},
            {'nombre': 'Marketing', 'semestres': [4, 5]},
            {'nombre': 'Finanzas', 'semestres': [5, 6]},
            {'nombre': 'Recursos Humanos', 'semestres': [6, 7]},
            {'nombre': 'Gestión de Proyectos', 'semestres': [7, 8]},
            {'nombre': 'Comercio Internacional', 'semestres': [6, 7]},
            {'nombre': 'Emprendimiento', 'semestres': [7, 8]},
            {'nombre': 'Estadística Comercial', 'semestres': [3, 4]},
            {'nombre': 'Economía', 'semestres': [2, 3]},
        ],
        'MECANICA': [
            {'nombre': 'Mecánica de Fluidos', 'semestres': [4, 5]},
            {'nombre': 'Termodinámica', 'semestres': [3, 4]},
            {'nombre': 'Resistencia de Materiales', 'semestres': [4, 5]},
            {'nombre': 'Máquinas Térmicas', 'semestres': [6, 7]},
            {'nombre': 'Diseño Mecánico', 'semestres': [5, 6]},
            {'nombre': 'Manufactura', 'semestres': [6, 7]},
            {'nombre': 'Vibración y Control', 'semestres': [7, 8]},
            {'nombre': 'Mecatrónica', 'semestres': [7, 8]},
            {'nombre': 'Física I', 'semestres': [1, 2]},
            {'nombre': 'Matemáticas I', 'semestres': [1, 2]},
        ],
        'QUIMICA': [
            {'nombre': 'Química General', 'semestres': [1, 2]},
            {'nombre': 'Química Orgánica', 'semestres': [2, 3]},
            {'nombre': 'Química Analítica', 'semestres': [3, 4]},
            {'nombre': 'Fisicoquímica', 'semestres': [4, 5]},
            {'nombre': 'Química Inorgánica', 'semestres': [3, 4]},
            {'nombre': 'Procesos Químicos', 'semestres': [5, 6]},
            {'nombre': 'Instrumentación Química', 'semestres': [6, 7]},
            {'nombre': 'Control de Procesos', 'semestres': [7, 8]},
            {'nombre': 'Laboratorio de Química', 'semestres': [2, 3, 4, 5]},
            {'nombre': 'Termodinámica Química', 'semestres': [4, 5]},
        ],
        'PETROLERA': [
            {'nombre': 'Geología del Petróleo', 'semestres': [3, 4]},
            {'nombre': 'Perforación', 'semestres': [5, 6]},
            {'nombre': 'Producción de Petróleo', 'semestres': [6, 7]},
            {'nombre': 'Refinación', 'semestres': [7, 8]},
            {'nombre': 'Yacimientos', 'semestres': [4, 5]},
            {'nombre': 'Completación de Pozos', 'semestres': [6, 7]},
            {'nombre': 'Evaluación de Formaciones', 'semestres': [5, 6]},
            {'nombre': 'Ingeniería de Reservorios', 'semestres': [7, 8]},
            {'nombre': 'Química del Petróleo', 'semestres': [3, 4]},
            {'nombre': 'Física del Petróleo', 'semestres': [2, 3]},
        ],
        'AMBIENTAL': [
            {'nombre': 'Ecología', 'semestres': [2, 3]},
            {'nombre': 'Química Ambiental', 'semestres': [3, 4]},
            {'nombre': 'Tratamiento de Aguas', 'semestres': [5, 6]},
            {'nombre': 'Gestión de Residuos', 'semestres': [6, 7]},
            {'nombre': 'Evaluación de Impacto Ambiental', 'semestres': [7, 8]},
            {'nombre': 'Microbiología Ambiental', 'semestres': [4, 5]},
            {'nombre': 'Contaminación Atmosférica', 'semestres': [6, 7]},
            {'nombre': 'Auditoría Ambiental', 'semestres': [7, 8]},
            {'nombre': 'Biotecnología Ambiental', 'semestres': [6, 7]},
            {'nombre': 'Legislación Ambiental', 'semestres': [5, 6]},
        ],
        'BIOTECNOLOGIA': [
            {'nombre': 'Biología Molecular', 'semestres': [3, 4]},
            {'nombre': 'Microbiología', 'semestres': [2, 3]},
            {'nombre': 'Bioquímica', 'semestres': [3, 4]},
            {'nombre': 'Ingeniería Genética', 'semestres': [6, 7]},
            {'nombre': 'Bioprocesos', 'semestres': [5, 6]},
            {'nombre': 'Inmunología', 'semestres': [4, 5]},
            {'nombre': 'Bioestadística', 'semestres': [4, 5]},
            {'nombre': 'Biotecnología Industrial', 'semestres': [7, 8]},
            {'nombre': 'Bioética', 'semestres': [6, 7]},
            {'nombre': 'Laboratorio de Biotecnología', 'semestres': [3, 4, 5, 6]},
        ]
    }
    
    # Contador de asignaturas agregadas
    total_agregadas = 0
    
    for carrera in carreras:
        carrera_nombre = carrera.nombre.upper()
        
        # Buscar asignaturas para esta carrera
        if carrera_nombre in asignaturas_por_carrera:
            asignaturas_data = asignaturas_por_carrera[carrera_nombre]
            
            print(f"\n📚 Procesando carrera: {carrera.get_nombre_display()}")
            
            for asignatura_data in asignaturas_data:
                nombre = asignatura_data['nombre']
                semestres = asignatura_data['semestres']
                
                for semestre in semestres:
                    # Verificar si ya existe esta asignatura para esta carrera y semestre
                    existe = Asignatura.objects.filter(
                        nombre=nombre,
                        carrera=carrera,
                        semestre=semestre
                    ).exists()
                    
                    if not existe:
                        # Crear la asignatura
                        Asignatura.objects.create(
                            nombre=nombre,
                            carrera=carrera,
                            semestre=semestre,
                            es_laboratorio=True,  # Por defecto para guías de laboratorio
                            creditos=4  # Valor por defecto
                        )
                        total_agregadas += 1
                        print(f"  ✅ Agregada: {nombre} - {semestre}° semestre")
                    else:
                        print(f"  ⏭️  Ya existe: {nombre} - {semestre}° semestre")
        else:
            print(f"⚠️  No hay datos para la carrera: {carrera_nombre}")
    
    print(f"\n🎉 ¡Completado! Se agregaron {total_agregadas} asignaturas de ejemplo.")
    print("Ahora puedes crear guías de laboratorio con asignaturas disponibles.")
    
    # Mostrar resumen
    print("\n📊 Resumen por carrera:")
    for carrera in carreras:
        count = Asignatura.objects.filter(carrera=carrera).count()
        print(f"  {carrera.get_nombre_display()}: {count} asignaturas")

if __name__ == "__main__":
    agregar_datos_ejemplo()
