#!/usr/bin/env python3
"""
Script para importar equipos directamente desde Excel 
manteniendo todas las columnas exactas del archivo
"""
import os
import sys
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import EquipoImportado

def main():
    print("🚀 Iniciando importación completa de equipos desde Excel...")
    
    # Leer archivo Excel
    excel_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'
    
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        print(f"📊 Archivo Excel leído: {len(df)} filas encontradas")
        
        # Mostrar las columnas para verificar
        print("📋 Columnas encontradas:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
            
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {e}")
        return
    
    # Filtrar solo registros de UALP si quieres solo La Paz
    df_ualp = df[df['UNIDAD ACADEMICA'] == 'UALP']
    print(f"🎯 Registros UALP encontrados: {len(df_ualp)}")
    
    if len(df_ualp) == 0:
        print("⚠️ No se encontraron registros para UALP")
        print("🔄 Importando todos los registros...")
        df_import = df
    else:
        print("✅ Importando solo registros UALP...")
        df_import = df_ualp
    
    print(f"📦 Total de registros a importar: {len(df_import)}")
    
    equipos_creados = 0
    equipos_actualizados = 0
    errores = 0
    
    for index, row in df_import.iterrows():
        try:
            # Mapear exactamente las columnas del Excel
            codigo = str(row.get('CODIGO', f'EQ-{index+1}'))
            
            # Buscar si ya existe
            equipo, created = EquipoImportado.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'numero': row.get('N') if pd.notna(row.get('N')) else None,
                    'unidad_academica': str(row.get('UNIDAD ACADEMICA', '')),
                    'responsable': str(row.get('RESPONSABLE', '')),
                    'ci': str(row.get('C.I.', '')),
                    'cargo': str(row.get('CARGO', '')),
                    'oficina': str(row.get('OFICINA', '')),
                    'descripcion_activo': str(row.get('DESCRIPCION DEL ACTIVO', '')),
                    'estado': str(row.get('ESTADO', '')),
                    'fecha_asignacion': str(row.get('FECHA DE ASIGNACION', '')),
                }
            )
            
            if created:
                equipos_creados += 1
            else:
                # Actualizar campos si ya existe
                equipo.numero = row.get('N') if pd.notna(row.get('N')) else None
                equipo.unidad_academica = str(row.get('UNIDAD ACADEMICA', ''))
                equipo.responsable = str(row.get('RESPONSABLE', ''))
                equipo.ci = str(row.get('C.I.', ''))
                equipo.cargo = str(row.get('CARGO', ''))
                equipo.oficina = str(row.get('OFICINA', ''))
                equipo.descripcion_activo = str(row.get('DESCRIPCION DEL ACTIVO', ''))
                equipo.estado = str(row.get('ESTADO', ''))
                equipo.fecha_asignacion = str(row.get('FECHA DE ASIGNACION', ''))
                equipo.save()
                equipos_actualizados += 1
            
            if (equipos_creados + equipos_actualizados) % 100 == 0:
                print(f"📈 Progreso: {equipos_creados} creados, {equipos_actualizados} actualizados...")
                
        except Exception as e:
            print(f"❌ Error en fila {index + 1}: {e}")
            errores += 1
            continue
    
    print(f"\n🎉 Importación completada!")
    print(f"✅ Equipos creados: {equipos_creados}")
    print(f"🔄 Equipos actualizados: {equipos_actualizados}")
    print(f"❌ Errores: {errores}")
    
    # Verificar el resultado por unidad académica
    print(f"\n📊 Resumen por unidad académica:")
    unidades = EquipoImportado.objects.values('unidad_academica').distinct()
    for unidad in unidades:
        count = EquipoImportado.objects.filter(unidad_academica=unidad['unidad_academica']).count()
        print(f"   {unidad['unidad_academica']}: {count} equipos")
    
    total_equipos = EquipoImportado.objects.count()
    print(f"\n📋 Total de equipos importados en base de datos: {total_equipos}")

if __name__ == "__main__":
    main()