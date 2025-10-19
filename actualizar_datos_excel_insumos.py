#!/usr/bin/env python
"""
Script para actualizar los insumos con los datos reales del Excel DATOS INSUMOS.xlsm
"""

import os
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from insumos.models import Insumo
from core.models import UnidadAcademica, Laboratorio, Carrera, Asignatura, UnidadTematica

def actualizar_insumos_desde_excel():
    """Actualiza los insumos con los datos del Excel"""
    
    # Leer Excel
    excel_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm"
    df = pd.read_excel(excel_path)
    
    print(f"📊 Leyendo {len(df)} registros del Excel...")
    print(f"Columnas disponibles: {list(df.columns)}")
    
    # Obtener la unidad académica UALP
    try:
        ualp = UnidadAcademica.objects.get(nombre='UALP')
        print(f"✅ Unidad UALP encontrada: {ualp}")
    except UnidadAcademica.DoesNotExist:
        print("❌ Error: Unidad UALP no encontrada en la base de datos")
        return
    
    # Primero, cambiar todos los insumos existentes de UACB a UALP
    print(f"\n🔄 Cambiando unidad académica de insumos existentes...")
    try:
        uacb = UnidadAcademica.objects.get(nombre='UACB')
        insumos_actualizados = Insumo.objects.filter(unidad_academica=uacb).update(unidad_academica=ualp)
        print(f"✅ {insumos_actualizados} insumos cambiados de UACB a UALP")
    except UnidadAcademica.DoesNotExist:
        print("⚠️ UACB no encontrada")
    
    # Ahora actualizar con datos del Excel
    insumos_procesados = 0
    errores = 0
    
    # Procesar cada fila del Excel
    for index, row in df.iterrows():
        try:
            # Extraer datos del Excel (manejar NaN)
            unidad_academica_excel = row['UNIDAD ACADÉMICA'] if pd.notna(row['UNIDAD ACADÉMICA']) else ''
            laboratorio_excel = row['LABORATORIO'] if pd.notna(row['LABORATORIO']) else ''
            categoria_excel = row['CATEGORÍA'] if pd.notna(row['CATEGORÍA']) else ''
            nombre = row['NOMBRE DEL ELEMENTO'] if pd.notna(row['NOMBRE DEL ELEMENTO']) else ''
            descripcion = row['DESCRIPCIÓN/CARACTERÍSTICAS'] if pd.notna(row['DESCRIPCIÓN/CARACTERÍSTICAS']) else ''
            marca_modelo = row['MARCA / MODELO'] if pd.notna(row['MARCA / MODELO']) else ''
            codigo = row['CÓDIGO DE INVENTARIO (INTERNO)'] if pd.notna(row['CÓDIGO DE INVENTARIO (INTERNO)']) else ''
            estado_excel = row['ESTADO'] if pd.notna(row['ESTADO']) else 'bueno'
            ubicacion = row['UBICACIÓN FÍSICA'] if pd.notna(row['UBICACIÓN FÍSICA']) else ''
            cantidad = row['CANTIDAD'] if pd.notna(row['CANTIDAD']) else 1.0
            unidad_medida_excel = row['UNIDAD DE MEDIDA'] if pd.notna(row['UNIDAD DE MEDIDA']) else ''
            fecha_ingreso = row['FECHA DE INGRESO/COMPRA'] if pd.notna(row['FECHA DE INGRESO/COMPRA']) else None
            uso_principal_excel = row['USO PRINCIPAL'] if pd.notna(row['USO PRINCIPAL']) else ''
            carrera_excel = row['CARRERA'] if pd.notna(row['CARRERA']) else ''
            observaciones = row['OBSERVACIONES'] if pd.notna(row['OBSERVACIONES']) else ''
            link_foto = row['INGRESE EL LINK DE LA FOTOGRAFIA DEL ELEMENTO'] if pd.notna(row['INGRESE EL LINK DE LA FOTOGRAFIA DEL ELEMENTO']) else ''
            
            # Mapear categorías del Excel a categorías del modelo
            categoria_bd = 'materiales'  # Por defecto
            if categoria_excel:
                if 'HERRAMIENTA' in categoria_excel.upper():
                    categoria_bd = 'herramientas'
                elif 'REACTIVO' in categoria_excel.upper():
                    categoria_bd = 'reactivos'
                elif 'MATERIAL' in categoria_excel.upper():
                    categoria_bd = 'materiales'
            
            # Mapear estados
            estado_bd = 'bueno'  # Por defecto
            if estado_excel:
                if 'OPERATIVO' in estado_excel.upper() or 'BUENO' in estado_excel.upper():
                    estado_bd = 'bueno'
                elif 'REGULAR' in estado_excel.upper():
                    estado_bd = 'regular'
                elif 'MALO' in estado_excel.upper():
                    estado_bd = 'malo'
                elif 'VENCIDO' in estado_excel.upper():
                    estado_bd = 'vencido'
                elif 'AGOTADO' in estado_excel.upper():
                    estado_bd = 'agotado'
            
            # Buscar insumo existente por nombre similar
            insumo = None
            if nombre:
                # Buscar por nombre exacto o similar
                insumos_candidatos = Insumo.objects.filter(
                    nombre_elemento__icontains=nombre[:30]  # Primeros 30 chars
                ).first()
                
                if insumos_candidatos:
                    insumo = insumos_candidatos
                else:
                    # Si no existe, tomar el primer insumo disponible para actualizar
                    # o crear uno nuevo si es necesario
                    insumo = Insumo.objects.filter(
                        nombre_elemento__in=['Sin nombre', 'ALICATE DE CORTE', 'BARRETA', 'BROCHA']
                    ).first()
            
            if insumo:
                # Actualizar con datos del Excel
                insumo.unidad_academica = ualp
                insumo.categoria = categoria_bd
                insumo.nombre_elemento = nombre or insumo.nombre_elemento
                insumo.descripcion_caracteristicas = descripcion
                insumo.marca_modelo = marca_modelo
                insumo.estado = estado_bd
                insumo.ubicacion_fisica = ubicacion
                insumo.cantidad = cantidad
                insumo.observaciones = observaciones
                
                # Convertir fecha si existe
                if fecha_ingreso and isinstance(fecha_ingreso, (pd.Timestamp, datetime)):
                    insumo.fecha_ingreso_compra = fecha_ingreso.date()
                
                insumo.save()
                insumos_procesados += 1
                
                if insumos_procesados % 20 == 0:
                    print(f"🔄 Procesados {insumos_procesados} insumos...")
            
        except Exception as e:
            errores += 1
            print(f"❌ Error en fila {index + 1}: {str(e)}")
            continue
    
    print(f"\n✅ Proceso completado!")
    print(f"📊 Insumos procesados: {insumos_procesados}")
    print(f"❌ Errores encontrados: {errores}")
    
    # Verificar algunos insumos actualizados
    print(f"\n🔍 Verificando insumos actualizados...")
    insumos_ualp = Insumo.objects.filter(unidad_academica__nombre='UALP')[:3]
    
    for insumo in insumos_ualp:
        print(f"  - ID {insumo.id}: {insumo.nombre_elemento} - {insumo.categoria} - {insumo.estado}")

if __name__ == "__main__":
    print("🚀 Iniciando actualización de insumos con datos del Excel...")
    actualizar_insumos_desde_excel()