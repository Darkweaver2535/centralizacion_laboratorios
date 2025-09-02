#!/usr/bin/env python
"""
Script para crear equipos básicos usando los datos curriculares reales ya importados
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *
from equipos.models import Equipo
from usuarios.models import Usuario
import random

def crear_equipos_basicos():
    """Crea equipos básicos usando los datos curriculares reales"""
    
    print("🚀 Creando equipos básicos con datos curriculares reales")
    print("=" * 60)
    
    # Verificar datos disponibles
    asignaturas = Asignatura.objects.all()
    laboratorios = Laboratorio.objects.all()
    criterios = CriterioDesempeno.objects.all()
    unidades_didacticas = UnidadDidactica.objects.all()
    contenidos = ContenidoAnalitico.objects.all()
    
    print(f"📊 Datos disponibles:")
    print(f"   - Asignaturas: {asignaturas.count()}")
    print(f"   - Laboratorios: {laboratorios.count()}")
    print(f"   - Criterios de Desempeño: {criterios.count()}")
    print(f"   - Unidades Didácticas: {unidades_didacticas.count()}")
    print(f"   - Contenidos Analíticos: {contenidos.count()}")
    
    if not asignaturas.exists():
        print("❌ No hay asignaturas disponibles")
        return
    
    if not laboratorios.exists():
        print("❌ No hay laboratorios disponibles")
        return
    
    # Obtener un usuario existente
    usuario = Usuario.objects.first()
    if not usuario:
        print("❌ No hay usuarios disponibles. Crear un superusuario primero.")
        return
    
    # Crear algunas guías de laboratorio básicas
    guias_creadas = []
    for i, asignatura in enumerate(asignaturas[:3]):  # Solo para las primeras 3 asignaturas
        guia, created = GuiaLaboratorio.objects.get_or_create(
            asignatura=asignatura,
            numero=1,
            defaults={
                'titulo': f'Guía de Laboratorio - {asignatura.get_nombre_display()}',
                'descripcion': f'Guía básica para {asignatura.get_nombre_display()}',
                'objetivos': f'Objetivos de laboratorio para {asignatura.get_nombre_display()}'
            }
        )
        if created:
            guias_creadas.append(guia)
    
    print(f"📖 Guías de laboratorio creadas: {len(guias_creadas)}")
    
    # Crear algunas prácticas básicas
    practicas_creadas = []
    for i, asignatura in enumerate(asignaturas[:3]):
        practica, created = Practica.objects.get_or_create(
            asignatura=asignatura,
            numero=1,
            defaults={
                'titulo': f'Práctica 1 - {asignatura.get_nombre_display()}',
                'descripcion': f'Primera práctica de {asignatura.get_nombre_display()}',
                'objetivos': f'Objetivos de la práctica de {asignatura.get_nombre_display()}',
                'duracion_horas': 2
            }
        )
        if created:
            practicas_creadas.append(practica)
    
    print(f"🧪 Prácticas creadas: {len(practicas_creadas)}")
    
    # Nombres de equipos reales típicos de laboratorios
    nombres_equipos = [
        "Microscopio óptico",
        "Multímetro digital",
        "Osciloscopio",
        "Fuente de alimentación",
        "Generador de funciones",
        "Balanza analítica",
        "pH-metro",
        "Conductímetro",
        "Computadora de escritorio",
        "Proyector multimedia",
        "Protoboard",
        "Kit de herramientas",
        "Voltímetro",
        "Amperímetro",
        "Termómetro digital"
    ]
    
    # Marcas y modelos reales
    marcas_modelos = [
        ("FLUKE", "87V"),
        ("TEKTRONIX", "TBS1052B"),
        ("KEYSIGHT", "E3631A"),
        ("METTLER TOLEDO", "ME204"),
        ("HANNA", "HI2020"),
        ("SAMSUNG", "LED Monitor"),
        ("EPSON", "EB-X41"),
        ("HP", "ProDesk 400"),
        ("DELL", "OptiPlex 3070"),
        ("AGILENT", "34401A"),
        ("BK PRECISION", "4040A"),
        ("RIGOL", "DG1022"),
        ("YOKOGAWA", "TY720"),
        ("EXTECH", "EX330"),
        ("OMEGA", "HH506RA")
    ]
    
    equipos_creados = 0
    errores = 0
    
    print("\n🔄 Creando equipos...")
    
    # Crear equipos para cada asignatura
    for asignatura in asignaturas:
        try:
            # Obtener datos relacionados
            criterios_asignatura = criterios.filter(asignatura=asignatura)
            unidades_asignatura = unidades_didacticas.filter(asignatura=asignatura)
            contenidos_asignatura = contenidos.filter(unidad_didactica__in=unidades_asignatura)
            
            # Seleccionar laboratorio (preferir de la misma unidad académica)
            laboratorio = laboratorios.filter(
                unidad_academica=asignatura.carrera.unidad_academica
            ).first()
            
            if not laboratorio:
                laboratorio = laboratorios.first()
            
            # Crear entre 3-5 equipos por asignatura
            num_equipos = random.randint(3, 5)
            
            for i in range(num_equipos):
                # Seleccionar datos aleatorios pero reales
                nombre_equipo = random.choice(nombres_equipos)
                marca, modelo = random.choice(marcas_modelos)
                
                criterio = criterios_asignatura.first() if criterios_asignatura.exists() else None
                unidad_didactica = unidades_asignatura.first() if unidades_asignatura.exists() else None
                contenido = contenidos_asignatura.first() if contenidos_asignatura.exists() else None
                
                # Buscar guía y práctica para esta asignatura
                guia = GuiaLaboratorio.objects.filter(asignatura=asignatura).first()
                practica = Practica.objects.filter(asignatura=asignatura).first()
                
                if not guia or not practica:
                    continue  # Saltar si no tiene guía o práctica
                
                # Crear equipo
                equipo = Equipo.objects.create(
                    # Campos obligatorios del modelo
                    unidad_academica=asignatura.carrera.unidad_academica,
                    carrera=asignatura.carrera,
                    semestre=asignatura.semestre,
                    asignatura=asignatura,
                    carga_horaria_semanal=asignatura.carga_horaria_semanal,
                    carga_horaria_semestral=asignatura.carga_horaria_semestral,
                    criterio_desempeno=criterio,
                    unidad_didactica=unidad_didactica,
                    contenido_analitico=contenido,
                    guia_laboratorio=guia,
                    practica=practica,
                    equipo_existente=f"{nombre_equipo} {i+1}",
                    marca=marca,
                    modelo=modelo,
                    estado=random.choice(['bueno', 'regular', 'malo']),
                    numero_unidades=random.randint(1, 3),
                    es_activo_fijo=random.choice([True, False]),
                    laboratorio=laboratorio,
                    seccion_area=f"Sección {random.choice(['A', 'B', 'C'])}",
                    identificador_aula=f"Aula {random.randint(101, 120)}",
                    equipo_requerido=f"Equipo complementario para {nombre_equipo}",
                    numero_equipos_requeridos=random.randint(0, 2),
                    usuario_creador=usuario,
                    responsable_excel="Coordinador de Laboratorio",
                    observaciones=f"Equipo para prácticas de {asignatura.get_nombre_display()}"
                )
                
                equipos_creados += 1
                
                if equipos_creados % 5 == 0:
                    print(f"⏳ Equipos creados: {equipos_creados}")
        
        except Exception as e:
            errores += 1
            print(f"❌ Error creando equipos para {asignatura}: {e}")
            if errores > 5:
                break
    
    # Estadísticas finales
    total_equipos = Equipo.objects.count()
    
    print("\n" + "=" * 60)
    print("🎉 Creación de equipos completada!")
    print(f"   ✅ Equipos creados: {equipos_creados}")
    print(f"   📊 Total en BD: {total_equipos}")
    print(f"   📖 Guías creadas: {len(guias_creadas)}")
    print(f"   🧪 Prácticas creadas: {len(practicas_creadas)}")
    print(f"   ⚠️ Errores: {errores}")
    print("\n✅ ¡Listo! Ahora la tabla debe mostrar datos.")

if __name__ == "__main__":
    crear_equipos_basicos()
