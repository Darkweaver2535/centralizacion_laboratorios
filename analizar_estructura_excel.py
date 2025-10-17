import pandas as pd

print("=== ANÁLISIS DE ESTRUCTURA DE DATOS EXCEL ===")

# Analizar archivo de equipos
print("\n1. ANÁLISIS DE DATOS EQUIPOS.xlsx")
archivo_equipos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'

try:
    df_equipos = pd.read_excel(archivo_equipos)
    print(f"Total filas: {len(df_equipos)}")
    print(f"Total columnas: {len(df_equipos.columns)}")
    print("\nNombres de columnas:")
    for i, col in enumerate(df_equipos.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\nPrimeras 3 filas como muestra:")
    print(df_equipos.head(3).to_string())
    
    print("\nColumnas con datos no nulos (primeras 100 filas):")
    for col in df_equipos.columns:
        non_null_count = df_equipos[col].head(100).notna().sum()
        print(f"{col}: {non_null_count}/100 valores no nulos")

except Exception as e:
    print(f"Error al leer archivo de equipos: {e}")

# Analizar archivo de insumos
print("\n\n2. ANÁLISIS DE DATOS INSUMOS.xlsm")
archivo_insumos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm'

try:
    df_insumos = pd.read_excel(archivo_insumos)
    print(f"Total filas: {len(df_insumos)}")
    print(f"Total columnas: {len(df_insumos.columns)}")
    print("\nNombres de columnas:")
    for i, col in enumerate(df_insumos.columns, 1):
        print(f"{i:2d}. {col}")
    
    print("\nPrimeras 3 filas como muestra:")
    print(df_insumos.head(3).to_string())
    
    print("\nColumnas con datos no nulos:")
    for col in df_insumos.columns:
        non_null_count = df_insumos[col].notna().sum()
        print(f"{col}: {non_null_count}/{len(df_insumos)} valores no nulos")

except Exception as e:
    print(f"Error al leer archivo de insumos: {e}")

print("\n=== ANÁLISIS COMPLETADO ===")