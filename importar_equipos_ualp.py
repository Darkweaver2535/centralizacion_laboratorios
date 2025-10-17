#!/usr/bin/env python3
"""
Script para importar equipos de UALP desde Excel
"""
import os
import sys
import django
import pandas as pd
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica
import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica
from django.contrib.auth.models import User

def main():
    print("🚀 Iniciando importación de equipos UALP...")
    
    # Buscar unidad académica UALP
    try:
        unidad_ualp = UnidadAcademica.objects.get(sigla='UALP')
        print(f"✅ Unidad académica encontrada: {unidad_ualp.sigla} (ID: {unidad_ualp.id})")
    except UnidadAcademica.DoesNotExist:
        print("❌ Error: No se encontró la unidad académica UALP")
        return
    
    # Leer archivo Excel
    excel_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'
    
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        print(f"📊 Archivo Excel leído: {len(df)} filas encontradas")
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {e}")
        return
    
    # Filtrar solo registros de UALP
    df_ualp = df[df['UNIDAD ACADEMICA'] == 'UALP']
    print(f"🎯 Registros UALP encontrados: {len(df_ualp)}")
    
    if len(df_ualp) == 0:
        print("⚠️ No se encontraron registros para UALP")
        return
    
    # Obtener o crear estados por defecto
    estado_activo, _ = EstadoEquipo.objects.get_or_create(
        nombre='Activo',
        defaults={'descripcion': 'Equipo en funcionamiento'}
    )
    
    estado_inactivo, _ = EstadoEquipo.objects.get_or_create(
        nombre='Inactivo',
        defaults={'descripcion': 'Equipo fuera de servicio'}
    )
    
    # Obtener o crear tipo por defecto
    tipo_general, _ = TipoEquipo.objects.get_or_create(
        nombre='General',
        defaults={'descripcion': 'Equipo de uso general'}
    )
    
    equipos_creados = 0
    errores = 0
    
    for index, row in df_ualp.iterrows():
        try:
            # Determinar estado basado en la columna ESTADO
            estado_texto = str(row.get('ESTADO', '')).strip().upper()
            if 'ACTIVO' in estado_texto or 'BUENO' in estado_texto or 'FUNCIONAL' in estado_texto:
                estado = estado_activo
            else:
                estado = estado_inactivo
            
            # Crear el equipo con toda la información como campos adicionales
            equipo = Equipo.objects.create(
                codigo=str(row.get('CODIGO', f'UALP-{index+1}')),
                nombre=str(row.get('DESCRIPCION DEL ACTIVO', 'Sin descripción'))[:200],
                descripcion=f"""
                Responsable: {row.get('RESPONSABLE', 'No especificado')}
                C.I.: {row.get('C.I.', 'No especificado')}
                Cargo: {row.get('CARGO', 'No especificado')}
                Oficina: {row.get('OFICINA', 'No especificado')}
                Fecha de Asignación: {row.get('FECHA DE ASIGNACION', 'No especificado')}
                Estado Original: {row.get('ESTADO', 'No especificado')}
                """.strip(),
                unidad_academica=unidad_ualp,
                tipo_equipo=tipo_general,
                estado=estado,
                precio=Decimal('0.00'),
                ubicacion=str(row.get('OFICINA', 'No especificado'))[:100]
            )
            
            equipos_creados += 1
            
            if equipos_creados % 100 == 0:
                print(f"📈 Progreso: {equipos_creados} equipos creados...")
                
        except Exception as e:
            print(f"❌ Error en fila {index + 1}: {e}")
            errores += 1
            continue
    
    print(f"\n🎉 Importación completada!")
    print(f"✅ Equipos creados: {equipos_creados}")
    print(f"❌ Errores: {errores}")
    
    # Verificar el resultado
    total_equipos_ualp = Equipo.objects.filter(unidad_academica=unidad_ualp).count()
    print(f"📊 Total de equipos UALP en base de datos: {total_equipos_ualp}")

if __name__ == "__main__":
    main()