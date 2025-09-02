#!/usr/bin/env python
"""
Script para crear datos de demostración con campos obligatorios correctos
"""

import os
import sys
import django
import random
from faker import Faker

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion_laboratorios.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, CriterioDesempeno
from equipos.models import (
    Laboratorio, TipoEquipo, CategoriaInsumo, EstadoEquipo,
    ResponsableEquipo, Equipo
)

def crear_datos_demo():
    """Crea datos de demostración completos"""
    
    print("🚀 Iniciando creación de datos de demostración")
    print("=" * 50)
    
    # Limpiar equipos existentes
    print("🧹 Limpiando equipos existentes...")
    Equipo.objects.all().delete()
    
    # Configurar Faker
    fake = Faker('es_ES')
    
    print("🔄 Creando datos de demostración...")
    
    # Obtener datos base
    unidades = list(UnidadAcademica.objects.all())
    carreras = list(Carrera.objects.all())
    
    print(f"Unidades disponibles: {len(unidades)}")
    print(f"Carreras disponibles: {len(carreras)}")
    
    if not unidades or not carreras:
        print("❌ No hay unidades académicas o carreras disponibles")
        return
    
    # Obtener o crear laboratorios
    laboratorios = []
    for unidad in unidades:
        lab, created = Laboratorio.objects.get_or_create(
            unidad_academica=unidad,
            nombre=f"Laboratorio {unidad.nombre}",
            defaults={
                'ubicacion': f"Edificio Central - {unidad.nombre}",
                'capacidad': random.randint(20, 40),
                'area_m2': random.randint(50, 120)
            }
        )
        laboratorios.append(lab)
    
    # Crear algunos tipos de equipo básicos
    tipos_equipo = [
        'Microscopio',
        'Multímetro',
        'Osciloscopio',
        'Computadora',
        'Proyector',
        'Balanza',
        'Centrífuga',
        'Espectrofotómetro'
    ]
    
    for tipo_nombre in tipos_equipo:
        TipoEquipo.objects.get_or_create(
            nombre=tipo_nombre,
            defaults={'descripcion': f'Tipo de equipo: {tipo_nombre}'}
        )
    
    # Crear estados básicos
    estados = ['Activo', 'Inactivo', 'En Mantenimiento', 'Dañado']
    for estado_nombre in estados:
        EstadoEquipo.objects.get_or_create(
            nombre=estado_nombre,
            defaults={'descripcion': f'Estado: {estado_nombre}'}
        )
    
    # Crear responsables básicos
    for i in range(5):
        ResponsableEquipo.objects.get_or_create(
            nombre=fake.name(),
            defaults={
                'cargo': random.choice(['Técnico', 'Coordinador', 'Encargado']),
                'email': fake.email(),
                'telefono': fake.phone_number()
            }
        )
    
    # Obtener objetos creados
    tipos = list(TipoEquipo.objects.all())
    estados = list(EstadoEquipo.objects.all())
    responsables = list(ResponsableEquipo.objects.all())
    
    # Lista de asignaturas básicas disponibles
    asignaturas_nombres = [
        'matematica_i', 'matematica_ii', 'fisica_i', 'fisica_ii',
        'quimica_general', 'programacion_i', 'programacion_ii',
        'dibujo_tecnico', 'introduccion_ingenieria', 'estadistica_probabilidades'
    ]
    
    # Crear asignaturas y datos relacionados
    asignaturas_creadas = []
    
    for carrera in carreras[:10]:  # Limitar a 10 carreras para no crear demasiados datos
        for i, asignatura_nombre in enumerate(asignaturas_nombres[:5]):  # 5 asignaturas por carrera
            semestre = (i % 8) + 1  # Distribuir en semestres 1-8
            
            # Crear asignatura
            asignatura, created = Asignatura.objects.get_or_create(
                nombre=asignatura_nombre,
                carrera=carrera,
                semestre=semestre,
                defaults={
                    'carga_horaria_semanal': random.randint(2, 6),
                    'carga_horaria_semestral': random.randint(40, 120)
                }
            )
            
            if created:
                # Crear unidad temática
                unidad_tematica, _ = UnidadTematica.objects.get_or_create(
                    asignatura=asignatura,
                    numero=1,
                    defaults={
                        'nombre': f'Unidad Temática - {asignatura.get_nombre_display()}',
                        'descripcion': f'Contenido principal de {asignatura.get_nombre_display()}'
                    }
                )
                
                # Crear criterio de desempeño
                criterio, _ = CriterioDesempeno.objects.get_or_create(
                    asignatura=asignatura,
                    codigo='CD001',
                    defaults={
                        'descripcion': f'Criterio de desempeño para {asignatura.get_nombre_display()}',
                        'unidad_tematica': unidad_tematica
                    }
                )
                
                asignaturas_creadas.append(asignatura)
    
    print(f"✅ Asignaturas creadas: {len(asignaturas_creadas)}")
    
    # Crear equipos
    equipos_creados = 0
    errores = 0
    
    for i in range(200):
        try:
            # Seleccionar datos aleatorios
            laboratorio = random.choice(laboratorios)
            tipo = random.choice(tipos)
            estado = random.choice(estados)
            responsable = random.choice(responsables)
            asignatura = random.choice(asignaturas_creadas) if asignaturas_creadas else None
            
            if not asignatura:
                print(f"❌ No hay asignaturas disponibles para equipo {i+1}")
                continue
            
            # Crear equipo con campos básicos
            equipo = Equipo.objects.create(
                nombre=f"{tipo.nombre} {fake.word().capitalize()} {i+1}",
                laboratorio=laboratorio,
                asignatura=asignatura,
                tipo_equipo=tipo,
                estado=estado,
                responsable=responsable,
                numero_unidades=random.randint(1, 5),
                # Solo campos que existen en el modelo
                observaciones=fake.text(max_nb_chars=200)
            )
            
            equipos_creados += 1
            
            if equipos_creados % 50 == 0:
                print(f"⏳ Equipos creados: {equipos_creados}")
            
        except Exception as e:
            errores += 1
            print(f"❌ Error creando equipo {i+1}: {e}")
            
            if errores > 10:  # Si hay más de 10 errores, parar
                print("❌ Demasiados errores, deteniendo creación")
                break
    
    # Contar totales
    total_equipos = Equipo.objects.count()
    
    print("\n" + "=" * 50)
    print("🎉 Demostración creada exitosamente!")
    print(f"   ✅ Equipos creados: {equipos_creados}")
    print(f"   📊 Total en BD: {total_equipos}")
    print(f"   🔍 Asignaturas: {len(asignaturas_creadas)}")
    print(f"   🏭 Laboratorios: {len(laboratorios)}")
    print(f"   ⚠️ Errores: {errores}")
    print("\n✅ ¡Listo para la demostración!")

if __name__ == "__main__":
    crear_datos_demo()
