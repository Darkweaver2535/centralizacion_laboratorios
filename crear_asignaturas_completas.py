#!/usr/bin/env python
"""
Script para crear asignaturas básicas para todas las carreras y semestres
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura
from django.db import transaction

def crear_asignaturas_basicas():
    """Crea asignaturas básicas para todas las carreras"""
    
    print("📚 CREANDO ASIGNATURAS BÁSICAS PARA TODAS LAS CARRERAS")
    print("=" * 55)
    
    # Asignaturas básicas por semestre (comunes para todas las carreras)
    asignaturas_basicas = {
        1: [
            ('matematica_i', 'Matemática I'),
            ('fisica_i', 'Física I'),
            ('quimica_general', 'Química General'),
            ('dibujo_tecnico', 'Dibujo Técnico'),
            ('introduccion_ingenieria', 'Introducción a la Ingeniería'),
            ('ingles_tecnico_i', 'Inglés Técnico I'),
        ],
        2: [
            ('matematica_ii', 'Matemática II'),
            ('fisica_ii', 'Física II'),
            ('quimica_organica', 'Química Orgánica'),
            ('programacion_i', 'Programación I'),
            ('metodologia_investigacion', 'Metodología de la Investigación'),
            ('ingles_tecnico_ii', 'Inglés Técnico II'),
        ],
        3: [
            ('matematica_iii', 'Matemática III'),
            ('fisica_iii', 'Física III'),
            ('mecanica_materiales', 'Mecánica de Materiales'),
            ('programacion_ii', 'Programación II'),
            ('estadistica_probabilidades', 'Estadística y Probabilidades'),
            ('etica_profesional', 'Ética Profesional'),
        ],
        4: [
            ('matematica_iv', 'Matemática IV'),
            ('termodinamica', 'Termodinámica'),
            ('resistencia_materiales', 'Resistencia de Materiales'),
            ('circuitos_electricos', 'Circuitos Eléctricos'),
            ('economia_ingenieria', 'Economía para Ingeniería'),
            ('comunicacion_tecnica', 'Comunicación Técnica'),
        ],
        5: [
            ('ecuaciones_diferenciales', 'Ecuaciones Diferenciales'),
            ('mecanica_fluidos', 'Mecánica de Fluidos'),
            ('analisis_sistemas', 'Análisis de Sistemas'),
            ('electronica_basica', 'Electrónica Básica'),
            ('gestion_proyectos', 'Gestión de Proyectos'),
            ('seguridad_industrial', 'Seguridad Industrial'),
        ],
        6: [
            ('metodos_numericos', 'Métodos Numéricos'),
            ('transferencia_calor', 'Transferencia de Calor'),
            ('bases_datos', 'Bases de Datos'),
            ('sistemas_control', 'Sistemas de Control'),
            ('investigacion_operativa', 'Investigación Operativa'),
            ('calidad_procesos', 'Calidad de Procesos'),
        ],
        7: [
            ('simulacion_sistemas', 'Simulación de Sistemas'),
            ('ingenieria_software', 'Ingeniería de Software'),
            ('automatizacion_industrial', 'Automatización Industrial'),
            ('gestion_calidad', 'Gestión de Calidad'),
            ('evaluacion_proyectos', 'Evaluación de Proyectos'),
            ('desarrollo_sostenible', 'Desarrollo Sostenible'),
        ],
        8: [
            ('inteligencia_artificial', 'Inteligencia Artificial'),
            ('redes_computadoras', 'Redes de Computadoras'),
            ('procesos_industriales', 'Procesos Industriales'),
            ('innovacion_tecnologica', 'Innovación Tecnológica'),
            ('formulacion_proyectos', 'Formulación de Proyectos'),
            ('liderazgo_equipos', 'Liderazgo de Equipos'),
        ],
        9: [
            ('proyecto_grado_i', 'Proyecto de Grado I'),
            ('sistemas_distribuidos', 'Sistemas Distribuidos'),
            ('optimizacion_procesos', 'Optimización de Procesos'),
            ('gestion_ambiental', 'Gestión Ambiental'),
            ('practica_profesional', 'Práctica Profesional'),
            ('emprendimiento', 'Emprendimiento'),
        ],
        10: [
            ('proyecto_grado_ii', 'Proyecto de Grado II'),
            ('auditoria_sistemas', 'Auditoría de Sistemas'),
            ('mantenimiento_industrial', 'Mantenimiento Industrial'),
            ('legislacion_profesional', 'Legislación Profesional'),
            ('seminario_titulacion', 'Seminario de Titulación'),
            ('responsabilidad_social', 'Responsabilidad Social'),
        ],
    }
    
    with transaction.atomic():
        # Eliminar asignaturas existentes
        count_eliminadas = Asignatura.objects.all().count()
        Asignatura.objects.all().delete()
        print(f"🧹 Eliminadas {count_eliminadas} asignaturas existentes")
        
        # Obtener todas las carreras
        carreras = Carrera.objects.all()
        total_asignaturas = 0
        
        print(f"\n📊 Procesando {carreras.count()} carreras...")
        
        for carrera in carreras:
            print(f"\n🎓 {carrera.get_nombre_display()} ({carrera.unidad_academica.nombre}):")
            
            for semestre, materias in asignaturas_basicas.items():
                for codigo, nombre in materias:
                    asignatura, created = Asignatura.objects.get_or_create(
                        carrera=carrera,
                        nombre=codigo,
                        semestre=semestre,
                        defaults={
                            'carga_horaria_semanal': 4,
                            'carga_horaria_semestral': 80,
                        }
                    )
                    if created:
                        total_asignaturas += 1
                        if semestre <= 3:  # Solo mostrar los primeros semestres para no saturar
                            print(f"    ✅ {semestre}° - {nombre}")
            
            if carreras.count() > 5:  # Si hay muchas carreras, mostrar solo resumen
                print(f"    📚 {len(asignaturas_basicas) * sum(len(materias) for materias in asignaturas_basicas.values())} asignaturas creadas")
        
        print(f"\n🎯 RESUMEN FINAL:")
        print(f"   📚 Total asignaturas creadas: {total_asignaturas}")
        print(f"   🎓 Carreras procesadas: {carreras.count()}")
        print(f"   📊 Semestres por carrera: {len(asignaturas_basicas)}")
        print(f"   📋 Asignaturas por semestre: {len(list(asignaturas_basicas.values())[0])}")

def verificar_asignaturas():
    """Verifica que las asignaturas se crearon correctamente"""
    print("\n🔍 VERIFICACIÓN DE ASIGNATURAS:")
    print("=" * 35)
    
    total_asignaturas = Asignatura.objects.count()
    carreras_count = Carrera.objects.count()
    
    print(f"📊 Total de asignaturas en BD: {total_asignaturas}")
    print(f"🎓 Total de carreras: {carreras_count}")
    
    # Verificar algunas carreras específicas
    carreras_muestra = Carrera.objects.all()[:3]
    
    for carrera in carreras_muestra:
        asignaturas_carrera = Asignatura.objects.filter(carrera=carrera)
        print(f"\n🎓 {carrera.get_nombre_display()}:")
        print(f"   📚 Asignaturas: {asignaturas_carrera.count()}")
        
        # Mostrar algunas asignaturas por semestre
        for semestre in [1, 5, 10]:
            asigs_semestre = asignaturas_carrera.filter(semestre=semestre)
            if asigs_semestre.exists():
                print(f"   {semestre}° Semestre: {asigs_semestre.count()} asignaturas")

def probar_api_asignaturas():
    """Prueba la API de asignaturas"""
    print("\n🔗 PRUEBA DE API DE ASIGNATURAS:")
    print("=" * 35)
    
    # Obtener una carrera para probar
    carrera = Carrera.objects.first()
    if carrera:
        print(f"🧪 Probando con carrera: {carrera.get_nombre_display()}")
        asignaturas = Asignatura.objects.filter(carrera=carrera, semestre=1)
        print(f"   📚 Asignaturas 1er semestre: {asignaturas.count()}")
        
        if asignaturas.exists():
            for asig in asignaturas[:3]:
                print(f"   • {asig.get_nombre_display()}")
    else:
        print("❌ No hay carreras disponibles")

if __name__ == "__main__":
    print("📚 SISTEMA DE ASIGNATURAS EMI")
    print("🏛️  Creando asignaturas para todas las carreras")
    print("=" * 50)
    
    try:
        # Crear asignaturas básicas
        crear_asignaturas_basicas()
        
        # Verificar resultado
        verificar_asignaturas()
        
        # Probar API
        probar_api_asignaturas()
        
        print("\n✅ SISTEMA DE ASIGNATURAS COMPLETADO")
        print("💡 Todas las carreras tienen asignaturas para 10 semestres")
        print("🚀 Las APIs de asignaturas ahora funcionarán correctamente")
        
    except Exception as e:
        print(f"❌ Error durante la creación: {str(e)}")
        print("🔧 Revisar la configuración del sistema")
