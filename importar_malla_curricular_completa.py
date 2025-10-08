import os
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    UnidadAcademica, Carrera, Asignatura, 
    CriterioDesempeno, UnidadDidactica, ContenidoAnalitico
)

def limpiar_texto(texto):
    """Limpia y normaliza texto"""
    if pd.isna(texto):
        return ""
    return str(texto).strip()

def importar_malla_curricular():
    excel_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS MALLA CURRICULAR.xlsx'
    
    print("=== IMPORTANDO MALLA CURRICULAR DESDE EXCEL ===")
    
    # Mapeo de nombres de carreras del Excel a la BD
    mapeo_carreras = {
        'INDUSTRIAL': 'ING_INDUSTRIAL',
        'MECÁNICA': 'ING_MECANICA', 
        'MECATRONICA': 'ING_MECATRONICA',
        'AUTOMOTRIZ': 'ING_AUTOMOTRIZ',
        'ELECTRÓNICA': 'ING_ELECTRONICA',
        'ELÉCTRICA': 'ING_ELECTRICA',
        'CIVIL': 'ING_CIVIL',
        'SISTEMAS': 'ING_SISTEMAS',
        'COMERCIAL': 'ING_COMERCIAL',
        'AMBIENTAL': 'ING_AMBIENTAL',
        'PETROLERA': 'ING_PETROLERA',
        'TELECOMUNICACIONES': 'ING_TELECOMUNICACIONES',
        'FINANCIERA': 'ING_FINANCIERA',
        'AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
        'AGRONOMICA': 'ING_AGRONOMICA',
        'GEOGRAFICA': 'ING_GEOGRAFICA',
        'SISTEMAS_ELECTRONICOS': 'ING_SISTEMAS_ELECTRONICOS'
    }
    
    # Leer Excel
    df = pd.read_excel(excel_path)
    print(f"📊 Registros en Excel: {len(df)}")
    
    # Contadores
    stats = {
        'asignaturas_procesadas': 0,
        'criterios_creados': 0,
        'unidades_creadas': 0,
        'contenidos_creados': 0,
        'errores': []
    }
    
    # Procesar fila por fila
    for index, row in df.iterrows():
        try:
            # Obtener datos básicos
            unidad_nombre = limpiar_texto(row['UNIDAD ACADEMICA'])
            carrera_nombre_excel = limpiar_texto(row['CARRERA'])
            asignatura_nombre = limpiar_texto(row['ASIGNATURA'])
            codigo_competencia = limpiar_texto(row['CODIGO DE COMPETENCIA'])
            sigla_curricular = limpiar_texto(row['SIGLA CURRICULAR'])
            criterio_texto = limpiar_texto(row['CRITERIO DE DESEMPEÑO'])
            unidad_texto = limpiar_texto(row['UNIDAD DIDACTICA'])
            contenido_texto = limpiar_texto(row['CONTENIDO ANALITICO'])
            
            # Mapear nombre de carrera del Excel al nombre en BD
            carrera_nombre = mapeo_carreras.get(carrera_nombre_excel, carrera_nombre_excel)
            
            # Validaciones básicas
            if not all([unidad_nombre, carrera_nombre_excel, asignatura_nombre]):
                print(f"⚠️  Fila {index+2}: Datos básicos incompletos")
                continue
                
            # Buscar Unidad Académica
            try:
                unidad_academica = UnidadAcademica.objects.get(nombre=unidad_nombre)
            except UnidadAcademica.DoesNotExist:
                stats['errores'].append(f"Fila {index+2}: Unidad Académica '{unidad_nombre}' no encontrada")
                continue
                
            # Buscar Carrera
            try:
                carrera = Carrera.objects.get(nombre=carrera_nombre, unidad_academica=unidad_academica)
            except Carrera.DoesNotExist:
                stats['errores'].append(f"Fila {index+2}: Carrera '{carrera_nombre}' (Excel: '{carrera_nombre_excel}') no encontrada en {unidad_nombre}")
                continue
                
            # Buscar o crear Asignatura
            asignatura, created = Asignatura.objects.get_or_create(
                nombre=asignatura_nombre,
                carrera=carrera,
                defaults={
                    'semestre': int(row['SEMESTRE']) if not pd.isna(row['SEMESTRE']) else 1,
                    'codigo_competencia': codigo_competencia,
                    'sigla_curricular': sigla_curricular,
                    'carga_horaria_semestral': int(row['CARGA HORARIA SEMESTRAL']) if not pd.isna(row['CARGA HORARIA SEMESTRAL']) else 0,
                    'carga_horaria_semanal': int(row['CARGA HORARIA SEMANAL']) if not pd.isna(row['CARGA HORARIA SEMANAL']) else 0,
                }
            )
            
            if created:
                stats['asignaturas_procesadas'] += 1
                print(f"✅ Asignatura: {asignatura_nombre} ({carrera_nombre_excel} → {carrera_nombre})")
            else:
                # Actualizar campos si la asignatura ya existe
                if codigo_competencia:
                    asignatura.codigo_competencia = codigo_competencia
                if sigla_curricular:
                    asignatura.sigla_curricular = sigla_curricular
                if not pd.isna(row['CARGA HORARIA SEMESTRAL']):
                    asignatura.carga_horaria_semestral = int(row['CARGA HORARIA SEMESTRAL'])
                if not pd.isna(row['CARGA HORARIA SEMANAL']):
                    asignatura.carga_horaria_semanal = int(row['CARGA HORARIA SEMANAL'])
                asignatura.save()
            
            # Crear Criterio de Desempeño (si no está vacío)
            if criterio_texto:
                criterio, created = CriterioDesempeno.objects.get_or_create(
                    nombre=criterio_texto[:200],  # Limitar a 200 caracteres
                    defaults={
                        'descripcion': criterio_texto,
                        'asignatura': asignatura
                    }
                )
                if created:
                    stats['criterios_creados'] += 1
                    
                # Crear Unidad Didáctica (si no está vacía)
                if unidad_texto:
                    unidad, created = UnidadDidactica.objects.get_or_create(
                        nombre=unidad_texto[:200],  # Limitar a 200 caracteres
                        defaults={
                            'descripcion': unidad_texto,
                            'asignatura': asignatura
                        }
                    )
                    if created:
                        stats['unidades_creadas'] += 1
                        
                    # Crear Contenido Analítico (si no está vacío)
                    if contenido_texto:
                        contenido, created = ContenidoAnalitico.objects.get_or_create(
                            nombre=contenido_texto[:300],  # Limitar a 300 caracteres
                            defaults={
                                'descripcion': contenido_texto,
                                'unidad_didactica': unidad
                            }
                        )
                        if created:
                            stats['contenidos_creados'] += 1
            
        except Exception as e:
            error_msg = f"Fila {index+2}: Error - {str(e)}"
            stats['errores'].append(error_msg)
            print(f"❌ {error_msg}")
    
    # Mostrar estadísticas finales
    print(f"\n=== RESUMEN DE IMPORTACIÓN ===")
    print(f"✅ Asignaturas procesadas: {stats['asignaturas_procesadas']}")
    print(f"✅ Criterios creados: {stats['criterios_creados']}")
    print(f"✅ Unidades didácticas creadas: {stats['unidades_creadas']}")
    print(f"✅ Contenidos analíticos creados: {stats['contenidos_creados']}")
    
    if stats['errores']:
        print(f"\n⚠️  ERRORES ENCONTRADOS ({len(stats['errores'])}):")
        for error in stats['errores'][:10]:  # Mostrar solo los primeros 10
            print(f"   - {error}")
        if len(stats['errores']) > 10:
            print(f"   ... y {len(stats['errores']) - 10} errores más")
    
    # Verificar estado final
    print(f"\n📊 ESTADO FINAL:")
    print(f"   Asignaturas: {Asignatura.objects.count()}")
    print(f"   Criterios de Desempeño: {CriterioDesempeno.objects.count()}")
    print(f"   Unidades Didácticas: {UnidadDidactica.objects.count()}")
    print(f"   Contenidos Analíticos: {ContenidoAnalitico.objects.count()}")

if __name__ == '__main__':
    importar_malla_curricular()