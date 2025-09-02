#!/usr/bin/env python
"""
Script para importar datos del archivo completo.xlsx
Solo importando las 9 columnas básicas para demo
"""
import os
import django
import pandas as pd
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, 
    GuiaLaboratorio, Practica, Laboratorio, CriterioDesempeno,
    UnidadDidactica, ContenidoAnalitico
)
from equipos.models import Equipo

def limpiar_base_datos():
    """Limpiar solo los equipos para reimportar"""
    print("🧹 Limpiando equipos existentes...")
    Equipo.objects.all().delete()
    print("✅ Equipos eliminados")

def mapear_unidad_academica(nombre_ua):
    """Mapear nombres de unidades académicas al formato correcto"""
    mapeo = {
        'UALP': 'UALP',
        'UACB': 'UACB', 
        'UASC': 'UASC',
        'UATP': 'UATP',
        'UARB': 'UARB',
        # Variaciones posibles
        'LA PAZ': 'UALP',
        'COCHABAMBA': 'UACB',
        'SANTA CRUZ': 'UASC',
        'TROPICO': 'UATP',
        'RIBERALTA': 'UARB'
    }
    
    nombre_limpio = str(nombre_ua).strip().upper()
    return mapeo.get(nombre_limpio, 'UALP')  # Default UALP

def mapear_carrera(nombre_carrera):
    """Mapear nombres de carreras al formato correcto"""
    mapeo = {
        'INGENIERÍA CIVIL': 'ING_CIVIL',
        'INGENIERIA CIVIL': 'ING_CIVIL',
        'ING_CIVIL': 'ING_CIVIL',
        'CIVIL': 'ING_CIVIL',
        
        'INGENIERÍA GEOGRÁFICA': 'ING_GEOGRAFICA',
        'INGENIERIA GEOGRAFICA': 'ING_GEOGRAFICA',
        'ING_GEOGRAFICA': 'ING_GEOGRAFICA',
        'GEOGRAFICA': 'ING_GEOGRAFICA',
        
        'INGENIERÍA EN SISTEMAS ELECTRÓNICOS': 'ING_SISTEMAS_ELECTRONICOS',
        'INGENIERIA EN SISTEMAS ELECTRONICOS': 'ING_SISTEMAS_ELECTRONICOS',
        'ING_SISTEMAS_ELECTRONICOS': 'ING_SISTEMAS_ELECTRONICOS',
        'SISTEMAS ELECTRONICOS': 'SISTEMAS_ELECTRONICOS',
        
        'INGENIERÍA INDUSTRIAL': 'ING_INDUSTRIAL',
        'INGENIERIA INDUSTRIAL': 'ING_INDUSTRIAL',
        'ING_INDUSTRIAL': 'ING_INDUSTRIAL',
        'INDUSTRIAL': 'ING_INDUSTRIAL',
        
        'INGENIERÍA COMERCIAL': 'ING_COMERCIAL',
        'INGENIERIA COMERCIAL': 'ING_COMERCIAL',
        'ING_COMERCIAL': 'ING_COMERCIAL',
        'COMERCIAL': 'ING_COMERCIAL',
        
        'INGENIERÍA DE SISTEMAS': 'ING_SISTEMAS',
        'INGENIERIA DE SISTEMAS': 'ING_SISTEMAS',
        'ING_SISTEMAS': 'ING_SISTEMAS',
        'SISTEMAS': 'ING_SISTEMAS',
        
        'INGENIERÍA AMBIENTAL': 'ING_AMBIENTAL',
        'INGENIERIA AMBIENTAL': 'ING_AMBIENTAL',
        'ING_AMBIENTAL': 'ING_AMBIENTAL',
        'AMBIENTAL': 'ING_AMBIENTAL',
        
        'INGENIERÍA PETROLERA': 'ING_PETROLERA',
        'INGENIERIA PETROLERA': 'ING_PETROLERA',
        'ING_PETROLERA': 'ING_PETROLERA',
        'PETROLERA': 'ING_PETROLERA',
        
        'INGENIERÍA MECATRÓNICA': 'ING_MECATRONICA',
        'INGENIERIA MECATRONICA': 'ING_MECATRONICA',
        'ING_MECATRONICA': 'ING_MECATRONICA',
        'MECATRONICA': 'ING_MECATRONICA',
        
        'INGENIERÍA EN TELECOMUNICACIONES': 'ING_TELECOMUNICACIONES',
        'INGENIERIA EN TELECOMUNICACIONES': 'ING_TELECOMUNICACIONES',
        'ING_TELECOMUNICACIONES': 'ING_TELECOMUNICACIONES',
        'TELECOMUNICACIONES': 'ING_TELECOMUNICACIONES',
        
        'INGENIERÍA FINANCIERA': 'ING_FINANCIERA',
        'INGENIERIA FINANCIERA': 'ING_FINANCIERA',
        'ING_FINANCIERA': 'ING_FINANCIERA',
        'FINANCIERA': 'ING_FINANCIERA',
        
        'INGENIERÍA AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
        'INGENIERIA AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
        'ING_AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
        'AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
        
        'INGENIERÍA AGRONÓMICA': 'ING_AGRONOMICA',
        'INGENIERIA AGRONOMICA': 'ING_AGRONOMICA',
        'ING_AGRONOMICA': 'ING_AGRONOMICA',
        'AGRONOMICA': 'ING_AGRONOMICA',
        
        'INFORMÁTICA': 'INFORMATICA',
        'INFORMATICA': 'INFORMATICA',
        
        'SISTEMAS ELECTRÓNICOS': 'SISTEMAS_ELECTRONICOS',
        'SISTEMAS ELECTRONICOS': 'SISTEMAS_ELECTRONICOS',
        
        'ENERGÍAS RENOVABLES': 'ENERGIAS_RENOVABLES',
        'ENERGIAS RENOVABLES': 'ENERGIAS_RENOVABLES',
        
        'CONSTRUCCIÓN CIVIL': 'CONSTRUCCION_CIVIL',
        'CONSTRUCCION CIVIL': 'CONSTRUCCION_CIVIL',
        
        'DISEÑO GRÁFICO Y COMUNICACIÓN AUDIOVISUAL': 'DISENO_GRAFICO',
        'DISEÑO GRAFICO Y COMUNICACION AUDIOVISUAL': 'DISENO_GRAFICO',
        'DISENO_GRAFICO': 'DISENO_GRAFICO'
    }
    
    nombre_limpio = str(nombre_carrera).strip().upper()
    return mapeo.get(nombre_limpio, 'ING_SISTEMAS')  # Default ING_SISTEMAS

def obtener_o_crear_objeto(modelo, nombre_campo, valor, defaults=None):
    """Función auxiliar para obtener o crear objetos"""
    if not valor or pd.isna(valor):
        return None
        
    valor_limpio = str(valor).strip()
    if not valor_limpio:
        return None
        
    try:
        kwargs = {nombre_campo: valor_limpio}
        if defaults:
            kwargs['defaults'] = defaults
        obj, created = modelo.objects.get_or_create(**kwargs)
        return obj
    except Exception as e:
        print(f"Error creando {modelo.__name__}: {e}")
        return None

def importar_excel():
    """Importar datos del archivo Excel"""
    archivo_excel = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/completo.xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo {archivo_excel}")
        return
    
    print(f"📁 Leyendo archivo: {archivo_excel}")
    
    try:
        df = pd.read_excel(archivo_excel)
        print(f"📊 Datos leídos: {len(df)} filas")
        print(f"📋 Columnas encontradas: {list(df.columns)}")
        
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return
    
    # Mapear columnas (usar las primeras 9 columnas básicas)
    columnas_mapeo = {
        0: 'unidad_academica',  # UNIDAD ACADÉMICA
        1: 'carrera',           # CARRERA  
        2: 'semestre',          # SEMESTRE
        3: 'asignatura',        # ASIGNATURA
        4: 'carga_horaria_semestral',  # CARGA HORARIA SEMESTRAL
        5: 'carga_horaria_semanal',    # CARGA HORARIA SEMANAL
        6: 'criterio_desempeno',       # CRITERIO DE DESEMPEÑO
        7: 'unidad_didactica',         # UNIDAD DIDACTICA
        8: 'contenido_analitico'       # CONTENIDO ANALITICO
    }
    
    equipos_creados = 0
    errores = 0
    
    print("🔄 Procesando filas...")
    
    for index, row in df.iterrows():
        try:
            # Solo usar las primeras 9 columnas
            if len(row) < 9:
                print(f"⚠️ Fila {index + 1}: Insuficientes columnas ({len(row)})")
                continue
                
            # Extraer datos básicos
            nombre_ua = row.iloc[0] if len(row) > 0 else None
            nombre_carrera = row.iloc[1] if len(row) > 1 else None
            semestre = row.iloc[2] if len(row) > 2 else None
            nombre_asignatura = row.iloc[3] if len(row) > 3 else None
            carga_semestral = row.iloc[4] if len(row) > 4 else None
            carga_semanal = row.iloc[5] if len(row) > 5 else None
            criterio_desemp = row.iloc[6] if len(row) > 6 else None
            unidad_did = row.iloc[7] if len(row) > 7 else None
            contenido_anal = row.iloc[8] if len(row) > 8 else None
            
            # Validar datos mínimos requeridos
            if not nombre_ua or pd.isna(nombre_ua):
                continue
            if not nombre_carrera or pd.isna(nombre_carrera):
                continue
                
            # Obtener/crear objetos relacionados
            codigo_ua = mapear_unidad_academica(nombre_ua)
            codigo_carrera = mapear_carrera(nombre_carrera)
            
            try:
                unidad_academica = UnidadAcademica.objects.get(nombre=codigo_ua)
            except UnidadAcademica.DoesNotExist:
                print(f"⚠️ Unidad académica no encontrada: {codigo_ua}")
                continue
                
            try:
                carrera = Carrera.objects.get(nombre=codigo_carrera)
            except Carrera.DoesNotExist:
                print(f"⚠️ Carrera no encontrada: {codigo_carrera}")
                continue
            
            # Crear objetos relacionados opcionales
            asignatura = obtener_o_crear_objeto(
                Asignatura, 'nombre', nombre_asignatura,
                {'carrera': carrera, 'descripcion': f'Asignatura {nombre_asignatura}'}
            ) if nombre_asignatura and not pd.isna(nombre_asignatura) else None
            
            criterio_desempeno = obtener_o_crear_objeto(
                CriterioDesempeno, 'descripcion', criterio_desemp
            ) if criterio_desemp and not pd.isna(criterio_desemp) else None
            
            unidad_didactica = obtener_o_crear_objeto(
                UnidadDidactica, 'nombre', unidad_did,
                {'descripcion': f'Unidad Didáctica {unidad_did}'}
            ) if unidad_did and not pd.isna(unidad_did) else None
            
            contenido_analitico = obtener_o_crear_objeto(
                ContenidoAnalitico, 'descripcion', contenido_anal
            ) if contenido_anal and not pd.isna(contenido_anal) else None
            
            # Crear el equipo con datos básicos
            equipo = Equipo.objects.create(
                # Campos obligatorios
                unidad_academica=unidad_academica,
                carrera=carrera,
                
                # Campos básicos de demo (9 columnas)
                semestre=semestre if semestre and not pd.isna(semestre) else None,
                asignatura=asignatura,
                carga_horaria_semestral=carga_semestral if carga_semestral and not pd.isna(carga_semestral) else None,
                carga_horaria_semanal=carga_semanal if carga_semanal and not pd.isna(carga_semanal) else None,
                criterio_desempeno=criterio_desempeno,
                unidad_didactica=unidad_didactica,
                contenido_analitico=contenido_analitico,
                
                # Campos adicionales en blanco para demostración
                equipo_existente=f"Equipo Demo {equipos_creados + 1}",
                marca="",
                modelo="",
                estado='bueno',  # Estado por defecto
                numero_unidades=1,
                es_activo_fijo=False,
                ubicacion_laboratorio=None,
                seccion_area="",
                identificador_aula="",
                equipo_requerido="",
                numero_equipos_requeridos=None,
                
                # Campos económicos en blanco
                costo_dolares=None,
                costo_bolivianos=None,
                
                # Campos de fechas en blanco
                fecha_adquisicion=None,
                fecha_instalacion=None,
                
                # Otros campos en blanco
                observaciones="",
                proveedor="",
                numero_serie="",
                codigo_inventario=f"DEMO-{equipos_creados + 1:06d}",
                responsable=None
            )
            
            equipos_creados += 1
            
            if equipos_creados % 100 == 0:
                print(f"✅ Procesados {equipos_creados} equipos...")
                
        except Exception as e:
            errores += 1
            print(f"❌ Error en fila {index + 1}: {e}")
            continue
    
    print(f"\n🎉 Importación completada:")
    print(f"   ✅ Equipos creados: {equipos_creados}")
    print(f"   ❌ Errores: {errores}")
    print(f"   📊 Total en BD: {Equipo.objects.count()}")

def mostrar_resumen():
    """Mostrar resumen de la importación"""
    print("\n" + "="*60)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*60)
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"   • Total equipos: {Equipo.objects.count()}")
    print(f"   • Total unidades académicas: {UnidadAcademica.objects.count()}")
    print(f"   • Total carreras: {Carrera.objects.count()}")
    print(f"   • Total asignaturas: {Asignatura.objects.count()}")
    
    print(f"\n📋 EQUIPOS POR UNIDAD ACADÉMICA:")
    for ua in UnidadAcademica.objects.all():
        count = Equipo.objects.filter(unidad_academica=ua).count()
        print(f"   • {ua.get_nombre_display()}: {count} equipos")
    
    print(f"\n📋 EQUIPOS POR CARRERA (Top 5):")
    for carrera in Carrera.objects.all()[:5]:
        count = Equipo.objects.filter(carrera=carrera).count()
        print(f"   • {carrera.get_nombre_display()}: {count} equipos")
    
    if Equipo.objects.exists():
        primer_equipo = Equipo.objects.first()
        print(f"\n🔍 EJEMPLO DE EQUIPO CREADO:")
        print(f"   • ID: {primer_equipo.id}")
        print(f"   • Nombre: {primer_equipo.equipo_existente}")
        print(f"   • Unidad: {primer_equipo.unidad_academica.get_nombre_display()}")
        print(f"   • Carrera: {primer_equipo.carrera.get_nombre_display()}")
        print(f"   • Código: {primer_equipo.codigo_inventario}")
    
    print("\n✅ Datos importados exitosamente para demostración!")
    print("🔧 Los usuarios pueden completar los campos faltantes usando el formulario de edición.")

if __name__ == '__main__':
    print("🚀 Iniciando importación de datos desde completo.xlsx")
    print("📋 Solo importando las 9 columnas básicas para demo")
    print("="*60)
    
    limpiar_base_datos()
    importar_excel()
    mostrar_resumen()
