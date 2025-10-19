#!/usr/bin/env python
"""
Script para actualizar los equipos existentes con los datos reales del Excel DATOS EQUIPOS.xlsx
"""

import os
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica

def actualizar_equipos_desde_excel():
    """Actualiza los equipos existentes con los datos del Excel"""
    
    # Leer Excel
    excel_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx"
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
    
    equipos_actualizados = 0
    errores = 0
    
    # Procesar cada fila del Excel
    for index, row in df.iterrows():
        try:
            # Extraer datos del Excel
            n = row['N']
            unidad_academica_excel = row['UNIDAD ACADEMICA']
            responsable = row['RESPONSABLE']
            ci = str(row['C.I.']) if pd.notna(row['C.I.']) else ''
            cargo = row['CARGO'] if pd.notna(row['CARGO']) else ''
            oficina = row['OFICINA'] if pd.notna(row['OFICINA']) else ''
            codigo = row['CODIGO'] if pd.notna(row['CODIGO']) else ''
            descripcion = row['DESCRIPCION DEL ACTIVO'] if pd.notna(row['DESCRIPCION DEL ACTIVO']) else ''
            estado_excel = row['ESTADO'] if pd.notna(row['ESTADO']) else 'bueno'
            fecha_asignacion = row['FECHA DE ASIGNACION'] if pd.notna(row['FECHA DE ASIGNACION']) else None
            
            # Convertir estado de Excel a formato BD
            estado_bd = 'bueno'
            if estado_excel:
                if estado_excel.lower() == 'regular':
                    estado_bd = 'regular'
                elif estado_excel.lower() == 'malo':
                    estado_bd = 'malo'
            
            # Buscar equipos que coincidan con el responsable y la descripción
            # o usar el nombre del equipo existente como descripción
            equipos_candidatos = Equipo.objects.filter(
                responsable_excel=responsable,
                equipo_existente__icontains=descripcion[:50]  # Primeros 50 chars
            ) | Equipo.objects.filter(
                responsable_excel=responsable,
                equipo_existente=descripcion
            )
            
            if not equipos_candidatos.exists():
                # Si no encuentra por descripción, buscar solo por responsable
                equipos_candidatos = Equipo.objects.filter(responsable_excel=responsable)
            
            if equipos_candidatos.exists():
                # Tomar el primer candidato y actualizarlo
                equipo = equipos_candidatos.first()
                
                # Actualizar con datos del Excel
                equipo.ci_responsable = ci
                equipo.cargo_responsable = cargo
                equipo.oficina = oficina
                equipo.codigo_excel = codigo
                equipo.descripcion_excel = descripcion
                equipo.estado = estado_bd
                
                # Convertir fecha si existe
                if fecha_asignacion and isinstance(fecha_asignacion, (pd.Timestamp, datetime)):
                    equipo.fecha_asignacion = fecha_asignacion.date()
                
                equipo.save()
                equipos_actualizados += 1
                
                if equipos_actualizados % 100 == 0:
                    print(f"🔄 Procesados {equipos_actualizados} equipos...")
            
        except Exception as e:
            errores += 1
            print(f"❌ Error en fila {index + 1}: {str(e)}")
            continue
    
    print(f"\n✅ Proceso completado!")
    print(f"📊 Equipos actualizados: {equipos_actualizados}")
    print(f"❌ Errores encontrados: {errores}")
    
    # Verificar algunos equipos actualizados
    print(f"\n🔍 Verificando equipos actualizados...")
    equipos_con_datos = Equipo.objects.exclude(ci_responsable='').exclude(ci_responsable__isnull=True)[:5]
    
    for equipo in equipos_con_datos:
        print(f"  - ID {equipo.id}: {equipo.responsable_excel} - CI: {equipo.ci_responsable}")

if __name__ == "__main__":
    print("🚀 Iniciando actualización de equipos con datos del Excel...")
    actualizar_equipos_desde_excel()