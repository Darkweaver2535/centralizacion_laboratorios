#!/usr/bin/env python
"""
Script para importar todas las asignaturas de Ingeniería Industrial desde el archivo Excel completo
Mantiene la estructura jerárquica: Asignatura -> CriterioDesempeno -> UnidadDidactica -> ContenidoAnalitico
"""

import os
import django
import pandas as pd
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico

def mapear_carrera_a_choice(carrera_excel):
    """Mapea el nombre de carrera del Excel al choice del modelo"""
    mapping = {
        'INDUSTRIAL': 'ING_INDUSTRIAL',
    }
    return mapping.get(carrera_excel, carrera_excel)

def mapear_asignatura_a_choice(nombre_asignatura):
    """Mapea el nombre de asignatura del Excel al choice del modelo"""
    # Para las asignaturas que ya están en los choices, usamos el código
    mapping = {
        'FISICA I': 'fisica_i',
        'FISICA II': 'fisica_ii', 
        'QUIMICA GENERAL': 'quimica_general',
        'FISICOQUIMICA': 'fisicoquimica',
        'QUÍMICA ORGÁNICA': 'quimica_organica',
        'MÉTODOS NUMÉRICOS E INFORMÁTICA': 'metodos_numericos',
        'TERMODINÁMICA': 'termodinamica',
        'SIMULACIÓN': 'simulacion_sistemas',
    }
    # Si no está en el mapping, usar el nombre tal como viene (para asignaturas nuevas)
    return mapping.get(nombre_asignatura, nombre_asignatura)

def limpiar_texto(texto):
    """Limpia y normaliza texto"""
    if pd.isna(texto):
        return ""
    return str(texto).strip()

def importar_malla_curricular():
    """Función principal de importación"""
    
    archivo = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/COMPLETO DATOS DE MALLA CURRICULAR_ing industrial.xlsb'
    
    print("🔄 Iniciando importación de malla curricular completa...")
    print(f"📁 Archivo: {archivo}")
    
    # Leer el archivo Excel
    try:
        df = pd.read_excel(archivo, sheet_name='Hoja1', engine='pyxlsb')
        print(f"✅ Archivo leído correctamente: {len(df)} filas")
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return
    
    # Estadísticas iniciales
    print(f"\n📊 ESTADÍSTICAS DEL ARCHIVO:")
    print(f"   Total filas: {len(df)}")
    print(f"   Asignaturas únicas: {df['ASIGNATURA'].nunique()}")
    print(f"   Criterios únicos: {df['CRITERIO DE DESEMPEÑO'].nunique()}")
    print(f"   Unidades didácticas únicas: {df['UNIDAD DIDACTICA'].nunique()}")
    print(f"   Contenidos analíticos únicos: {df['CONTENIDO ANALITICO'].nunique()}")
    
    # Verificar y obtener unidad académica y carrera
    try:
        unidad_academica = UnidadAcademica.objects.get(nombre='UALP')
        carrera_choice = mapear_carrera_a_choice('INDUSTRIAL')
        carrera = Carrera.objects.get(unidad_academica=unidad_academica, nombre=carrera_choice)
        print(f"✅ Usando: {unidad_academica} - {carrera}")
    except Exception as e:
        print(f"❌ Error obteniendo unidad académica o carrera: {e}")
        return
    
    # Contadores para estadísticas
    stats = {
        'asignaturas_creadas': 0,
        'asignaturas_actualizadas': 0,
        'criterios_creados': 0,
        'unidades_creadas': 0,
        'contenidos_creados': 0,
        'errores': 0
    }
    
    # Procesar datos agrupados por asignatura
    asignaturas_data = df.groupby(['ASIGNATURA', 'SEMESTRE'])
    
    print(f"\n🔄 Procesando {len(asignaturas_data)} asignaturas...")
    
    for (nombre_asignatura, semestre), grupo_asignatura in asignaturas_data:
        try:
            with transaction.atomic():
                print(f"\n📚 Procesando: {nombre_asignatura} (Semestre {semestre})")
                
                # Obtener información adicional de la asignatura
                primera_fila = grupo_asignatura.iloc[0]
                codigo_competencia = limpiar_texto(primera_fila['CODIGO DSE COMPETENCIA'])
                sigla_curricular = limpiar_texto(primera_fila['SIGLA CURRICULAR'])
                carga_horaria_semestral = primera_fila['CARGA HORARIA SEMESTRAL']
                carga_horaria_semanal = primera_fila['CARGA HORARIA SEMANAL']
                
                # Crear o actualizar asignatura
                nombre_choice = mapear_asignatura_a_choice(nombre_asignatura)
                
                asignatura, created = Asignatura.objects.get_or_create(
                    nombre=nombre_choice,
                    carrera=carrera,
                    semestre=semestre,
                    defaults={
                        'codigo_competencia': codigo_competencia,
                        'sigla_curricular': sigla_curricular,
                        'carga_horaria_semestral': carga_horaria_semestral if pd.notna(carga_horaria_semestral) else 0,
                        'carga_horaria_semanal': carga_horaria_semanal if pd.notna(carga_horaria_semanal) else 0,
                    }
                )
                
                if created:
                    stats['asignaturas_creadas'] += 1
                    print(f"   ✅ Asignatura creada")
                else:
                    stats['asignaturas_actualizadas'] += 1
                    print(f"   ℹ️  Asignatura ya existía")
                
                # Procesar criterios de desempeño para esta asignatura
                criterios_data = grupo_asignatura.groupby('CRITERIO DE DESEMPEÑO')
                
                for descripcion_criterio, grupo_criterio in criterios_data:
                    descripcion_criterio = limpiar_texto(descripcion_criterio)
                    if not descripcion_criterio:
                        continue
                        
                    # Crear criterio de desempeño
                    # Usar descripción como nombre y añadir prefijo de asignatura para evitar duplicados
                    nombre_criterio = f"{nombre_asignatura[:20]} - {descripcion_criterio[:150]}"
                    
                    criterio, created = CriterioDesempeno.objects.get_or_create(
                        asignatura=asignatura,
                        descripcion=descripcion_criterio,
                        defaults={
                            'nombre': nombre_criterio
                        }
                    )
                    
                    if created:
                        stats['criterios_creados'] += 1
                        print(f"     ➕ Criterio creado: {descripcion_criterio[:50]}...")
                    
                    # Procesar unidades didácticas para este criterio
                    unidades_data = grupo_criterio.groupby('UNIDAD DIDACTICA')
                    
                    for nombre_unidad, grupo_unidad in unidades_data:
                        nombre_unidad = limpiar_texto(nombre_unidad)
                        if not nombre_unidad:
                            continue
                            
                        # Crear unidad didáctica
                        unidad_didactica, created = UnidadDidactica.objects.get_or_create(
                            asignatura=asignatura,
                            nombre=nombre_unidad,
                            defaults={
                                'descripcion': f'Unidad didáctica: {nombre_unidad}'
                            }
                        )
                        
                        if created:
                            stats['unidades_creadas'] += 1
                            print(f"       ➕ Unidad creada: {nombre_unidad}")
                        
                        # Procesar contenidos analíticos para esta unidad
                        for _, fila in grupo_unidad.iterrows():
                            contenido_analitico = limpiar_texto(fila['CONTENIDO ANALITICO'])
                            if not contenido_analitico:
                                continue
                                
                            # Crear contenido analítico
                            # Añadir prefijo de unidad para evitar duplicados globales
                            nombre_contenido = f"{nombre_unidad[:30]} - {contenido_analitico}"[:300]
                            
                            contenido, created = ContenidoAnalitico.objects.get_or_create(
                                nombre=nombre_contenido,
                                defaults={
                                    'unidad_didactica': unidad_didactica,
                                    'descripcion': contenido_analitico
                                }
                            )
                            
                            if created:
                                stats['contenidos_creados'] += 1
                                print(f"         ➕ Contenido creado: {contenido_analitico[:40]}...")
                
        except Exception as e:
            stats['errores'] += 1
            print(f"   ❌ Error procesando {nombre_asignatura}: {e}")
            continue
    
    # Mostrar estadísticas finales
    print(f"\n✅ IMPORTACIÓN COMPLETADA")
    print(f"📊 ESTADÍSTICAS FINALES:")
    print(f"   Asignaturas creadas: {stats['asignaturas_creadas']}")
    print(f"   Asignaturas actualizadas: {stats['asignaturas_actualizadas']}")
    print(f"   Criterios de desempeño creados: {stats['criterios_creados']}")
    print(f"   Unidades didácticas creadas: {stats['unidades_creadas']}")
    print(f"   Contenidos analíticos creados: {stats['contenidos_creados']}")
    print(f"   Errores: {stats['errores']}")
    
    # Verificación final
    print(f"\n🔍 VERIFICACIÓN EN BASE DE DATOS:")
    total_asignaturas = Asignatura.objects.filter(carrera=carrera).count()
    total_criterios = CriterioDesempeno.objects.filter(asignatura__carrera=carrera).count()
    total_unidades = UnidadDidactica.objects.filter(asignatura__carrera=carrera).count()
    total_contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura__carrera=carrera).count()
    
    print(f"   Total asignaturas en BD: {total_asignaturas}")
    print(f"   Total criterios en BD: {total_criterios}")
    print(f"   Total unidades en BD: {total_unidades}")
    print(f"   Total contenidos en BD: {total_contenidos}")

if __name__ == "__main__":
    try:
        importar_malla_curricular()
    except KeyboardInterrupt:
        print("\n❌ Importación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()