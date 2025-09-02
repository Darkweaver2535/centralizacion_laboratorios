#!/usr/bin/env python
"""
Script para importar datos de malla curricular desde Excel
Archivo: pruebas/DATOS DE MALLA CURRICULAR.xlsx

Columnas esperadas:
- UNIDAD ACADEMICA
- CARRERA  
- SEMESTRE
- ASIGNATURA
- CODIGO DSE COMPETENCIA
- SIGLA CURRICULAR
- CARGA HORARIA SEMESTRAL
- CARGA HORARIA SEMANAL
- CRITERIO DE DESEMPEÑO
- UNIDAD DIDACTICA
- CONTENIDO ANALITICO
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
from core.models import UnidadAcademica, Carrera, Asignatura, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico
from django.db import transaction

def leer_excel_malla_curricular():
    """Lee el archivo Excel de malla curricular"""
    archivo_excel = 'pruebas/DATOS DE MALLA CURRICULAR.xlsx'
    
    if not os.path.exists(archivo_excel):
        print(f"❌ No se encontró el archivo: {archivo_excel}")
        return None
    
    try:
        # Leer el Excel
        df = pd.read_excel(archivo_excel)
        print(f"✅ Archivo leído exitosamente: {len(df)} filas")
        
        # Mostrar información del archivo
        print(f"\n📊 Columnas encontradas ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i}. {col}")
        
        # Mostrar primeras filas
        print(f"\n📋 Primeras 3 filas:")
        print(df.head(3).to_string())
        
        return df
        
    except Exception as e:
        print(f"❌ Error al leer el archivo: {str(e)}")
        return None

def analizar_datos_existentes(df):
    """Analiza qué datos ya existen en la BD"""
    print(f"\n🔍 ANÁLISIS DE DATOS EXISTENTES")
    print("="*50)
    
    # Analizar Unidades Académicas
    unidades_excel = df['UNIDAD ACADEMICA'].unique() if 'UNIDAD ACADEMICA' in df.columns else []
    unidades_bd = list(UnidadAcademica.objects.values_list('nombre', flat=True))
    
    print(f"\n📚 UNIDADES ACADÉMICAS:")
    print(f"  En Excel: {len(unidades_excel)}")
    print(f"  En BD: {len(unidades_bd)}")
    
    for unidad in unidades_excel:
        existe = any(unidad.upper() in bd_unidad.upper() for bd_unidad in unidades_bd)
        status = "✅" if existe else "❌"
        print(f"  {status} {unidad}")
    
    # Analizar Carreras
    carreras_excel = df['CARRERA'].unique() if 'CARRERA' in df.columns else []
    carreras_bd = list(Carrera.objects.values_list('nombre', flat=True))
    
    print(f"\n🎓 CARRERAS:")
    print(f"  En Excel: {len(carreras_excel)}")
    print(f"  En BD: {len(carreras_bd)}")
    
    for carrera in carreras_excel:
        existe = any(carrera.upper() in bd_carrera.upper() for bd_carrera in carreras_bd)
        status = "✅" if existe else "❌"
        print(f"  {status} {carrera}")
    
    # Analizar Asignaturas
    asignaturas_excel = df['ASIGNATURA'].unique() if 'ASIGNATURA' in df.columns else []
    asignaturas_bd = list(Asignatura.objects.values_list('nombre', flat=True))
    
    print(f"\n📖 ASIGNATURAS:")
    print(f"  En Excel: {len(asignaturas_excel)}")
    print(f"  En BD: {len(asignaturas_bd)}")
    
    nuevas_asignaturas = []
    for asignatura in asignaturas_excel[:10]:  # Mostrar solo las primeras 10
        existe = any(asignatura.upper() in bd_asignatura.upper() for bd_asignatura in asignaturas_bd)
        status = "✅" if existe else "❌"
        print(f"  {status} {asignatura}")
        if not existe:
            nuevas_asignaturas.append(asignatura)
    
    if len(asignaturas_excel) > 10:
        print(f"  ... y {len(asignaturas_excel) - 10} más")

def verificar_nuevos_campos(df):
    """Verifica qué campos nuevos necesitamos agregar al modelo"""
    print(f"\n🆕 NUEVOS CAMPOS DETECTADOS")
    print("="*50)
    
    campos_nuevos = []
    
    if 'CODIGO DSE COMPETENCIA' in df.columns:
        codigos = df['CODIGO DSE COMPETENCIA'].dropna().unique()
        print(f"\n📝 CODIGO DSE COMPETENCIA:")
        print(f"  Valores únicos: {len(codigos)}")
        print(f"  Ejemplos: {list(codigos[:5])}")
        campos_nuevos.append('codigo_dse_competencia')
    
    if 'SIGLA CURRICULAR' in df.columns:
        siglas = df['SIGLA CURRICULAR'].dropna().unique()
        print(f"\n🔤 SIGLA CURRICULAR:")
        print(f"  Valores únicos: {len(siglas)}")
        print(f"  Ejemplos: {list(siglas[:5])}")
        campos_nuevos.append('sigla_curricular')
    
    return campos_nuevos

def proponer_estructura_modelo(campos_nuevos):
    """Propone la estructura del modelo para los nuevos campos"""
    print(f"\n🏗️ PROPUESTA DE ESTRUCTURA DE MODELO")
    print("="*50)
    
    print(f"\n📋 Campos que necesitamos agregar al modelo Asignatura:")
    
    if 'codigo_dse_competencia' in campos_nuevos:
        print(f"""
    # Campo para código DSE de competencia
    codigo_dse_competencia = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='Código DSE Competencia',
        help_text='Código de competencia del DSE'
    )""")
    
    if 'sigla_curricular' in campos_nuevos:
        print(f"""
    # Campo para sigla curricular
    sigla_curricular = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='Sigla Curricular',
        help_text='Sigla curricular de la asignatura'
    )""")

def main():
    print("🚀 IMPORTADOR DE MALLA CURRICULAR")
    print("="*50)
    
    # Leer archivo Excel
    df = leer_excel_malla_curricular()
    if df is None:
        return
    
    # Analizar datos existentes
    analizar_datos_existentes(df)
    
    # Verificar nuevos campos
    campos_nuevos = verificar_nuevos_campos(df)
    
    # Proponer estructura
    proponer_estructura_modelo(campos_nuevos)
    
    print(f"\n📋 RESUMEN:")
    print(f"  ✅ Archivo leído: {len(df)} registros")
    print(f"  🆕 Campos nuevos detectados: {len(campos_nuevos)}")
    print(f"  📝 Próximo paso: Extender modelo Asignatura con nuevos campos")

if __name__ == "__main__":
    main()
