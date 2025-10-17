#!/usr/bin/env python
"""
Script para importar equipos e insumos desde archivos Excel
"""
import os
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from insumos.models import Insumo
from core.models import UnidadAcademica, Carrera, Asignatura

def limpiar_datos_existentes():
    """Limpiar equipos e insumos existentes"""
    print("Limpiando datos existentes...")
    Equipo.objects.all().delete()
    Insumo.objects.all().delete()
    print("Datos limpiados.")

def mapear_unidad_academica(unidad_excel):
    """Mapear nombres de unidades del Excel a las del sistema"""
    mapeo = {
        'UALP': 'UALP',
        'UACB': 'UACB',
        'UASC': 'UASC',
        'UATP': 'UATP',
        'UARB': 'UARB',
    }
    
    # Buscar coincidencias parciales
    unidad_upper = str(unidad_excel).upper().strip()
    for key in mapeo.keys():
        if key in unidad_upper:
            return mapeo[key]
    
    # Por defecto UALP si no se encuentra
    print(f"Unidad no encontrada: {unidad_excel}, asignando UALP")
    return 'UALP'

def importar_equipos():
    """Importar equipos desde DATOS EQUIPOS.xlsx"""
    print("\n=== IMPORTANDO EQUIPOS ===")
    file_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx"
    
    try:
        df = pd.read_excel(file_path, sheet_name='Hoja1')
        print(f"Archivo leído correctamente. Total filas: {len(df)}")
        
        equipos_creados = 0
        errores = 0
        
        for index, row in df.iterrows():
            try:
                # Obtener datos del Excel
                unidad_excel = row.get('UNIDAD ACADEMICA', 'UALP')
                nombre_equipo = row.get('DESCRIPCION DEL ACTIVO', f'Equipo {index+1}')
                codigo = row.get('CODIGO', '')
                estado = row.get('ESTADO', 'Regular')
                responsable = row.get('RESPONSABLE', '')
                
                # Limpiar y validar datos
                if pd.isna(nombre_equipo) or str(nombre_equipo).strip() == '':
                    nombre_equipo = f'Equipo {index+1}'
                
                # Mapear unidad académica
                unidad_codigo = mapear_unidad_academica(unidad_excel)
                
                try:
                    unidad_obj = UnidadAcademica.objects.get(nombre=unidad_codigo)
                except UnidadAcademica.DoesNotExist:
                    print(f"Unidad {unidad_codigo} no existe, usando UALP")
                    unidad_obj = UnidadAcademica.objects.get(nombre='UALP')
                
                # Crear equipo
                carrera_default = Carrera.objects.filter(nombre='ING_INDUSTRIAL').first() or Carrera.objects.first()
                asignatura_default = Asignatura.objects.first()
                
                equipo = Equipo.objects.create(
                    unidad_academica=unidad_obj,
                    carrera=carrera_default,
                    semestre=1,  # Valor por defecto
                    asignatura=asignatura_default,
                    carga_horaria_semanal=4,  # Valor por defecto
                    carga_horaria_semestral=64,  # Valor por defecto
                    equipo_existente=str(nombre_equipo).strip()[:200],  # Campo correcto
                    marca=str(codigo)[:100],  # Usar código como marca temporalmente
                    modelo=str(estado)[:100],  # Usar estado como modelo temporalmente
                    estado='bueno' if estado == 'Regular' else 'regular',
                    numero_unidades=1,  # Valor por defecto
                    es_activo_fijo=True,  # Valor por defecto
                    ubicacion=str(responsable)[:200],  # Usar responsable como ubicación temporalmente
                    numero_equipos_requeridos=1  # Valor por defecto
                )
                
                equipos_creados += 1
                
                if equipos_creados % 100 == 0:
                    print(f"Procesados {equipos_creados} equipos...")
                    
            except Exception as e:
                errores += 1
                print(f"Error en fila {index+1}: {e}")
                continue
        
        print(f"Equipos importados: {equipos_creados}")
        print(f"Errores: {errores}")
        
    except Exception as e:
        print(f"Error al leer archivo de equipos: {e}")

def importar_insumos():
    """Importar insumos desde DATOS INSUMOS.xlsm"""
    print("\n=== IMPORTANDO INSUMOS ===")
    file_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm"
    
    try:
        df = pd.read_excel(file_path, sheet_name='REGISTRO')
        print(f"Archivo leído correctamente. Total filas: {len(df)}")
        
        insumos_creados = 0
        errores = 0
        
        for index, row in df.iterrows():
            try:
                # Obtener datos del Excel
                unidad_excel = row.get('UNIDAD ACADÉMICA', 'UALP')
                nombre_insumo = row.get('NOMBRE DEL ELEMENTO', f'Insumo {index+1}')
                categoria = row.get('CATEGORÍA', 'Material')
                descripcion = row.get('DESCRIPCIÓN/CARACTERÍSTICAS', '')
                marca = row.get('MARCA / MODELO', '')
                cantidad = row.get('CANTIDAD', 1)
                estado = row.get('ESTADO', 'Bueno')
                
                # Limpiar y validar datos
                if pd.isna(nombre_insumo) or str(nombre_insumo).strip() == '':
                    nombre_insumo = f'Insumo {index+1}'
                
                if pd.isna(categoria) or str(categoria).strip() == '':
                    categoria = 'Material'
                
                # Mapear unidad académica
                unidad_codigo = mapear_unidad_academica(unidad_excel)
                
                try:
                    unidad_obj = UnidadAcademica.objects.get(nombre=unidad_codigo)
                except UnidadAcademica.DoesNotExist:
                    print(f"Unidad {unidad_codigo} no existe, usando UALP")
                    unidad_obj = UnidadAcademica.objects.get(nombre='UALP')
                
                # Crear insumo
                carrera_default = Carrera.objects.filter(nombre='ING_INDUSTRIAL').first() or Carrera.objects.first()
                asignatura_default = Asignatura.objects.first()
                
                insumo = Insumo.objects.create(
                    unidad_academica=unidad_obj,
                    carrera=carrera_default,
                    categoria=str(categoria).strip()[:100] if categoria else 'materiales',
                    nombre_elemento=str(nombre_insumo).strip()[:200],  # Campo correcto
                    descripcion_caracteristicas=f"{descripcion}. Marca: {marca}. Estado: {estado}",  # Campo correcto
                    marca_modelo=str(marca)[:200] if marca else '',  # Campo correcto
                    estado=estado.lower() if estado and estado.lower() in ['bueno', 'regular', 'malo', 'vencido', 'agotado'] else 'bueno',
                    cantidad=int(cantidad) if not pd.isna(cantidad) and str(cantidad).isdigit() else 1
                )
                
                insumos_creados += 1
                
                if insumos_creados % 20 == 0:
                    print(f"Procesados {insumos_creados} insumos...")
                    
            except Exception as e:
                errores += 1
                print(f"Error en fila {index+1}: {e}")
                continue
        
        print(f"Insumos importados: {insumos_creados}")
        print(f"Errores: {errores}")
        
    except Exception as e:
        print(f"Error al leer archivo de insumos: {e}")

def verificar_importacion():
    """Verificar que los datos se importaron correctamente"""
    print("\n=== VERIFICACIÓN POST-IMPORTACIÓN ===")
    
    print(f"Total equipos: {Equipo.objects.count()}")
    print(f"Total insumos: {Insumo.objects.count()}")
    
    print("\n=== DISTRIBUCIÓN POR UNIDAD ===")
    for unidad in UnidadAcademica.objects.all():
        equipos_count = Equipo.objects.filter(unidad_academica=unidad).count()
        insumos_count = Insumo.objects.filter(unidad_academica=unidad).count()
        print(f"{unidad.nombre}: {equipos_count} equipos, {insumos_count} insumos")

def main():
    print("=== IMPORTACIÓN DE DATOS DE EQUIPOS E INSUMOS ===")
    print(f"Fecha: {datetime.now()}")
    
    # Limpiar datos existentes
    limpiar_datos_existentes()
    
    # Importar equipos
    importar_equipos()
    
    # Importar insumos
    importar_insumos()
    
    # Verificar importación
    verificar_importacion()
    
    print("\n=== IMPORTACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()