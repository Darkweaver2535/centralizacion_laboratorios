#!/usr/bin/env python
"""
Script para importar datos de malla curricular desde Excel
Archivo: pruebas/DATOS DE MALLA CURRICULAR.xlsx

Este script importa:
- Asignaturas con sus nuevos campos (código de competencia, sigla curricular)
- Criterios de desempeño específicos por asignatura
- Unidades didácticas específicas por asignatura  
- Contenidos analíticos específicos por asignatura
"""

import os
import sys
import django
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

import pandas as pd
from core.models import (
    UnidadAcademica, Carrera, Asignatura, 
    CriterioDesempeno, UnidadDidactica, ContenidoAnalitico
)
from django.db import transaction
import re

def normalizar_nombre_asignatura(nombre):
    """Convierte nombre de asignatura a formato del modelo"""
    mapa_normalizacion = {
        'FISICA I': 'fisica_i',
        'FISICA II': 'fisica_ii', 
        'QUIMICA GENERAL': 'quimica_general',
        'FISICOQUIMICA': 'fisicoquimica',
    }
    return mapa_normalizacion.get(nombre.upper(), nombre.lower().replace(' ', '_'))

def normalizar_carrera(nombre):
    """Convierte nombre de carrera a formato del modelo"""
    mapa_carreras = {
        'INDUSTRIAL': 'ING_INDUSTRIAL',
        'CIVIL': 'ING_CIVIL',
        'PETROLERA': 'ING_PETROLERA',
        'ELECTRICA': 'ING_ELECTRICA',
        'ELECTRONICA': 'ING_ELECTRONICA',
    }
    return mapa_carreras.get(nombre.upper(), nombre.upper())

def normalizar_unidad_academica(nombre):
    """Convierte nombre de unidad académica a formato del modelo"""
    mapa_unidades = {
        'UALP': 'UALP',
        'UARB': 'UARB',
    }
    return mapa_unidades.get(nombre.upper(), nombre.upper())

def limpiar_texto(texto):
    """Limpia texto eliminando caracteres especiales y normalizando espacios"""
    if pd.isna(texto):
        return ""
    
    texto = str(texto).strip()
    # Reemplazar múltiples espacios y saltos de línea por uno solo
    texto = re.sub(r'\s+', ' ', texto)
    # Eliminar caracteres especiales pero mantener puntuación básica
    texto = re.sub(r'[^\w\s\.,;:-]', '', texto)
    return texto

def importar_malla_curricular():
    """Función principal de importación"""
    print("🚀 IMPORTACIÓN DE MALLA CURRICULAR")
    print("="*50)
    
    archivo_excel = 'pruebas/DATOS DE MALLA CURRICULAR.xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ No se encontró el archivo: {archivo_excel}")
        return
    
    try:
        # Leer Excel
        df = pd.read_excel(archivo_excel)
        print(f"✅ Archivo leído: {len(df)} registros")
        
        # Estadísticas iniciales
        stats = {
            'asignaturas_creadas': 0,
            'asignaturas_actualizadas': 0,
            'criterios_creados': 0,
            'unidades_creadas': 0,
            'contenidos_creados': 0,
            'errores': 0
        }
        
        with transaction.atomic():
            print("\n📋 Procesando registros...")
            
            for index, row in df.iterrows():
                try:
                    # Obtener datos básicos
                    unidad_nombre = normalizar_unidad_academica(row['UNIDAD ACADEMICA'])
                    carrera_nombre = normalizar_carrera(row['CARRERA'])
                    semestre = int(row['SEMESTRE'])
                    asignatura_nombre = normalizar_nombre_asignatura(row['ASIGNATURA'])
                    
                    print(f"  Procesando: {row['ASIGNATURA']} - {carrera_nombre} - Sem {semestre}")
                    
                    # Buscar unidad académica
                    try:
                        unidad_academica = UnidadAcademica.objects.get(nombre=unidad_nombre)
                    except UnidadAcademica.DoesNotExist:
                        print(f"    ⚠️ Unidad académica no encontrada: {unidad_nombre}")
                        continue
                    
                    # Buscar carrera
                    try:
                        carrera = Carrera.objects.get(
                            unidad_academica=unidad_academica, 
                            nombre=carrera_nombre
                        )
                    except Carrera.DoesNotExist:
                        print(f"    ⚠️ Carrera no encontrada: {carrera_nombre}")
                        continue
                    
                    # Crear o actualizar asignatura
                    asignatura, created = Asignatura.objects.get_or_create(
                        nombre=asignatura_nombre,
                        carrera=carrera,
                        semestre=semestre,
                        defaults={
                            'carga_horaria_semanal': int(row['CARGA HORARIA SEMANAL']) if pd.notna(row['CARGA HORARIA SEMANAL']) else 4,
                            'carga_horaria_semestral': int(row['CARGA HORARIA SEMESTRAL']) if pd.notna(row['CARGA HORARIA SEMESTRAL']) else 80,
                            'codigo_competencia': str(row['CODIGO DE COMPETENCIA']) if pd.notna(row['CODIGO DE COMPETENCIA']) else '',
                            'sigla_curricular': str(row['SIGLA CURRICULAR']) if pd.notna(row['SIGLA CURRICULAR']) else '',
                        }
                    )
                    
                    if created:
                        stats['asignaturas_creadas'] += 1
                        print(f"    ✅ Asignatura creada: {asignatura}")
                    else:
                        # Actualizar campos si no están vacíos
                        actualizado = False
                        if pd.notna(row['CODIGO DE COMPETENCIA']) and not asignatura.codigo_competencia:
                            asignatura.codigo_competencia = str(row['CODIGO DE COMPETENCIA'])
                            actualizado = True
                        if pd.notna(row['SIGLA CURRICULAR']) and not asignatura.sigla_curricular:
                            asignatura.sigla_curricular = str(row['SIGLA CURRICULAR'])
                            actualizado = True
                        if actualizado:
                            asignatura.save()
                            stats['asignaturas_actualizadas'] += 1
                            print(f"    🔄 Asignatura actualizada: {asignatura}")
                    
                    # Procesar criterio de desempeño
                    if pd.notna(row['CRITERIO DE DESEMPEÑO']):
                        criterio_texto = limpiar_texto(row['CRITERIO DE DESEMPEÑO'])
                        criterio, created = CriterioDesempeno.objects.get_or_create(
                            asignatura=asignatura,
                            nombre=criterio_texto[:200],  # Truncar si es muy largo
                            defaults={
                                'descripcion': criterio_texto
                            }
                        )
                        if created:
                            stats['criterios_creados'] += 1
                            print(f"    ✅ Criterio creado: {criterio.nombre[:50]}...")
                    
                    # Procesar unidad didáctica
                    if pd.notna(row['UNIDAD DIDACTICA']):
                        unidad_texto = limpiar_texto(row['UNIDAD DIDACTICA'])
                        unidad_didactica, created = UnidadDidactica.objects.get_or_create(
                            asignatura=asignatura,
                            nombre=unidad_texto[:200],  # Truncar si es muy largo
                            defaults={
                                'descripcion': unidad_texto
                            }
                        )
                        if created:
                            stats['unidades_creadas'] += 1
                            print(f"    ✅ Unidad didáctica creada: {unidad_didactica.nombre[:50]}...")
                    
                    # Procesar contenido analítico (relacionado con unidad didáctica)
                    if pd.notna(row['CONTENIDO ANALITICO']) and pd.notna(row['UNIDAD DIDACTICA']):
                        contenido_texto = limpiar_texto(row['CONTENIDO ANALITICO'])
                        unidad_didactica_nombre = limpiar_texto(row['UNIDAD DIDACTICA'])
                        
                        # Buscar la unidad didáctica correspondiente
                        try:
                            unidad_didactica_obj = UnidadDidactica.objects.get(
                                asignatura=asignatura,
                                nombre=unidad_didactica_nombre[:200]
                            )
                            contenido, created = ContenidoAnalitico.objects.get_or_create(
                                unidad_didactica=unidad_didactica_obj,
                                nombre=contenido_texto[:300],  # Usar nombre en lugar de descripcion
                                defaults={
                                    'descripcion': contenido_texto
                                }
                            )
                            if created:
                                stats['contenidos_creados'] += 1
                                print(f"    ✅ Contenido analítico creado: {contenido.nombre[:50]}...")
                        except UnidadDidactica.DoesNotExist:
                            print(f"    ⚠️ No se encontró unidad didáctica: {unidad_didactica_nombre[:50]}...")
                            continue
                
                except Exception as e:
                    stats['errores'] += 1
                    print(f"    ❌ Error en fila {index + 1}: {str(e)}")
                    continue
        
        # Mostrar estadísticas finales
        print(f"\n📊 RESUMEN DE IMPORTACIÓN")
        print("="*50)
        print(f"✅ Asignaturas creadas: {stats['asignaturas_creadas']}")
        print(f"🔄 Asignaturas actualizadas: {stats['asignaturas_actualizadas']}")
        print(f"✅ Criterios de desempeño creados: {stats['criterios_creados']}")
        print(f"✅ Unidades didácticas creadas: {stats['unidades_creadas']}")
        print(f"✅ Contenidos analíticos creados: {stats['contenidos_creados']}")
        print(f"❌ Errores: {stats['errores']}")
        
        print(f"\n🎯 DATOS FINALES EN BASE DE DATOS:")
        print(f"  📚 Total asignaturas: {Asignatura.objects.count()}")
        print(f"  🎯 Total criterios: {CriterioDesempeno.objects.count()}")
        print(f"  📋 Total unidades didácticas: {UnidadDidactica.objects.count()}")
        print(f"  📝 Total contenidos analíticos: {ContenidoAnalitico.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")

if __name__ == "__main__":
    importar_malla_curricular()
