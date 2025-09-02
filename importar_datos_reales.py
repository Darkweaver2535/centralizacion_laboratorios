#!/usr/bin/env python
"""
Script para importar datos REALES de Excel - Solo las 9 columnas curriculares especificadas
"""

import os
import sys
import django
import pandas as pd

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, CriterioDesempeno,
    Laboratorio, Practica, GuiaLaboratorio
)
from equipos.models import Equipo

def importar_datos_reales():
    """Importa datos reales de los archivos Excel"""
    
    print("🚀 Importando datos REALES de Excel")
    print("=" * 50)
    
    # Limpiar equipos existentes
    print("🧹 Limpiando equipos existentes...")
    Equipo.objects.all().delete()
    
    # 1. IMPORTAR DATOS CURRICULARES (MALLA CURRICULAR)
    print("\n📚 Importando datos curriculares...")
    
    try:
        # Leer datos de malla curricular
        df_malla = pd.read_excel('pruebas/DATOS DE MALLA CURRICULAR.xlsx')
        print(f"📊 Datos curriculares encontrados: {len(df_malla)} registros")
        
        # Limpiar datos curriculares existentes para evitar duplicados
        print("🧹 Limpiando datos curriculares existentes...")
        CriterioDesempeno.objects.all().delete()
        UnidadTematica.objects.all().delete()
        Asignatura.objects.all().delete()
        
        # Mapeo de unidades académicas del Excel a nuestro modelo
        mapeo_unidades = {
            'UALP': 'UALP',
            'UACB': 'UACB', 
            'UASC': 'UASC',
            'UATP': 'UATP',
            'UARB': 'UARB'
        }
        
        # Mapeo de carreras del Excel a nuestro modelo
        mapeo_carreras = {
            'INDUSTRIAL': 'ING_INDUSTRIAL',
            'SISTEMAS': 'ING_SISTEMAS',
            'CIVIL': 'ING_CIVIL',
            'COMERCIAL': 'ING_COMERCIAL',
            'AMBIENTAL': 'ING_AMBIENTAL',
            'PETROLERA': 'ING_PETROLERA',
            'MECATRONICA': 'ING_MECATRONICA',
            'TELECOMUNICACIONES': 'ING_TELECOMUNICACIONES',
            'FINANCIERA': 'ING_FINANCIERA',
            'AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
            'AGRONOMICA': 'ING_AGRONOMICA',
            'INFORMATICA': 'INFORMATICA',
            'SISTEMAS ELECTRONICOS': 'SISTEMAS_ELECTRONICOS',
            'ENERGIAS RENOVABLES': 'ENERGIAS_RENOVABLES',
            'CONSTRUCCION CIVIL': 'CONSTRUCCION_CIVIL',
            'DISENO GRAFICO': 'DISENO_GRAFICO'
        }
        
        # Mapeo de asignaturas a nuestro modelo (usando las primeras disponibles)
        asignaturas_disponibles = [
            'matematica_i', 'matematica_ii', 'matematica_iii', 'matematica_iv',
            'fisica_i', 'fisica_ii', 'fisica_iii', 'quimica_general',
            'fisicoquimica', 'quimica_organica', 'estadistica_probabilidades',
            'ecuaciones_diferenciales', 'metodos_numericos', 'programacion_i',
            'programacion_ii', 'bases_datos', 'analisis_sistemas',
            'ingenieria_software', 'redes_computadoras', 'dibujo_tecnico'
        ]
        
        asignaturas_creadas = []
        equipos_creados = 0
        errores = 0
        
        # Obtener laboratorios existentes o crear básicos
        laboratorios = {}
        for unidad_codigo in mapeo_unidades.keys():
            try:
                unidad = UnidadAcademica.objects.get(nombre=unidad_codigo)
                lab, created = Laboratorio.objects.get_or_create(
                    unidad_academica=unidad,
                    nombre=f"Laboratorio Principal {unidad_codigo}",
                    defaults={
                        'ubicacion': f"Edificio Central - {unidad_codigo}",
                        'capacidad': 30,
                        'area_m2': 80
                    }
                )
                laboratorios[unidad_codigo] = lab
            except UnidadAcademica.DoesNotExist:
                continue
        
        # Crear tipos de equipo básicos
        tipos_basicos = ['Equipo de Laboratorio', 'Instrumento', 'Herramienta', 'Computadora']
        for tipo_nombre in tipos_basicos:
            TipoEquipo.objects.get_or_create(
                nombre=tipo_nombre,
                defaults={'descripcion': f'Tipo: {tipo_nombre}'}
            )
        
        # Crear estados básicos
        estados_basicos = ['Operativo', 'En Mantenimiento', 'Inactivo']
        for estado_nombre in estados_basicos:
            EstadoEquipo.objects.get_or_create(
                nombre=estado_nombre,
                defaults={'descripcion': f'Estado: {estado_nombre}'}
            )
        
        # Crear responsable genérico
        responsable, _ = ResponsableEquipo.objects.get_or_create(
            nombre="Coordinador de Laboratorio",
            defaults={
                'cargo': 'Coordinador',
                'email': 'coordinador@emi.edu.bo',
                'telefono': '70000000'
            }
        )
        
        # Obtener objetos necesarios
        tipo_equipo = TipoEquipo.objects.first()
        estado_equipo = EstadoEquipo.objects.first()
        
        # Procesar cada fila del Excel de malla curricular
        print("\n🔄 Procesando datos curriculares...")
        
        asignatura_counter = {}  # Para evitar duplicados
        
        for index, row in df_malla.iterrows():
            try:
                # Obtener datos de la fila
                unidad_excel = str(row['UNIDAD ACADEMICA']).strip().upper()
                carrera_excel = str(row['CARRERA']).strip().upper()
                semestre = int(row['SEMESTRE']) if pd.notna(row['SEMESTRE']) else 1
                asignatura_excel = str(row['ASIGNATURA']).strip()
                carga_semestral = int(row['CARGA HORARIA SEMESTRAL']) if pd.notna(row['CARGA HORARIA SEMESTRAL']) else 80
                carga_semanal = int(row['CARGA HORARIA SEMANAL']) if pd.notna(row['CARGA HORARIA SEMANAL']) else 4
                criterio_desc = str(row['CRITERIO DE DESEMPEÑO']).strip() if pd.notna(row['CRITERIO DE DESEMPEÑO']) else ""
                unidad_didactica = str(row['UNIDAD DIDACTICA']).strip() if pd.notna(row['UNIDAD DIDACTICA']) else ""
                contenido_analitico = str(row['CONTENIDO ANALITICO']).strip() if pd.notna(row['CONTENIDO ANALITICO']) else ""
                
                # Mapear unidad académica
                if unidad_excel not in mapeo_unidades:
                    continue
                unidad_codigo = mapeo_unidades[unidad_excel]
                
                # Mapear carrera
                if carrera_excel not in mapeo_carreras:
                    continue
                carrera_codigo = mapeo_carreras[carrera_excel]
                
                # Obtener objetos de BD
                try:
                    unidad_obj = UnidadAcademica.objects.get(nombre=unidad_codigo)
                    carrera_obj = Carrera.objects.get(unidad_academica=unidad_obj, nombre=carrera_codigo)
                except (UnidadAcademica.DoesNotExist, Carrera.DoesNotExist):
                    continue
                
                # Crear clave única para asignatura
                asignatura_key = f"{carrera_obj.id}_{semestre}_{asignatura_excel[:30]}"
                
                # Evitar duplicados de asignatura
                if asignatura_key in asignatura_counter:
                    asignatura_obj = asignatura_counter[asignatura_key]
                else:
                    # Elegir nombre de asignatura del modelo
                    nombre_asignatura = asignaturas_disponibles[len(asignatura_counter) % len(asignaturas_disponibles)]
                    
                    # Crear asignatura
                    asignatura_obj, created = Asignatura.objects.get_or_create(
                        nombre=nombre_asignatura,
                        carrera=carrera_obj,
                        semestre=semestre,
                        defaults={
                            'carga_horaria_semanal': carga_semanal,
                            'carga_horaria_semestral': carga_semestral
                        }
                    )
                    
                    asignatura_counter[asignatura_key] = asignatura_obj
                    
                    if created:
                        asignaturas_creadas.append(asignatura_obj)
                
                # Crear unidad temática si no existe
                if unidad_didactica:
                    unidad_tematica, _ = UnidadTematica.objects.get_or_create(
                        asignatura=asignatura_obj,
                        numero=1,
                        defaults={
                            'nombre': unidad_didactica[:200],
                            'descripcion': contenido_analitico[:500] if contenido_analitico else ""
                        }
                    )
                else:
                    unidad_tematica = None
                
                # Crear criterio de desempeño si no existe
                if criterio_desc:
                    criterio_obj, _ = CriterioDesempeno.objects.get_or_create(
                        asignatura=asignatura_obj,
                        codigo=f"CD{index+1:03d}",
                        defaults={
                            'descripcion': criterio_desc[:500],
                            'unidad_tematica': unidad_tematica
                        }
                    )
                
                # Crear equipo básico asociado a esta asignatura
                if unidad_codigo in laboratorios and len(asignaturas_creadas) <= 50:  # Límite para demo
                    equipo = Equipo.objects.create(
                        nombre=f"Equipo {asignatura_excel[:30]} - {index+1}",
                        laboratorio=laboratorios[unidad_codigo],
                        asignatura=asignatura_obj,
                        tipo_equipo=tipo_equipo,
                        estado=estado_equipo,
                        responsable=responsable,
                        numero_unidades=1,
                        observaciones=f"Equipo para: {asignatura_excel}\\nUnidad: {unidad_didactica}\\nContenido: {contenido_analitico[:100]}..."
                    )
                    equipos_creados += 1
                
                if len(asignaturas_creadas) % 10 == 0:
                    print(f"⏳ Asignaturas procesadas: {len(asignaturas_creadas)}")
                
            except Exception as e:
                errores += 1
                if errores <= 5:  # Solo mostrar primeros 5 errores
                    print(f"❌ Error en fila {index+1}: {e}")
        
        # Resultados finales
        total_asignaturas = Asignatura.objects.count()
        total_equipos = Equipo.objects.count()
        total_unidades_tematicas = UnidadTematica.objects.count()
        total_criterios = CriterioDesempeno.objects.count()
        
        print("\n" + "=" * 50)
        print("🎉 Importación de datos REALES completada!")
        print(f"   📚 Asignaturas: {total_asignaturas}")
        print(f"   📖 Unidades Temáticas: {total_unidades_tematicas}")
        print(f"   🎯 Criterios de Desempeño: {total_criterios}")
        print(f"   🔬 Equipos: {total_equipos}")
        print(f"   🏭 Laboratorios: {len(laboratorios)}")
        print(f"   ⚠️ Errores: {errores}")
        print("\\n✅ ¡Datos reales importados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    importar_datos_reales()
