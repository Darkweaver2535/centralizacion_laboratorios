import pandas as pd
import os

def analizar_equipos():
    print("=== ANÁLISIS DE DATOS EQUIPOS.xlsx ===")
    try:
        file_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx"
        
        # Leer el archivo Excel
        xl = pd.ExcelFile(file_path)
        print(f"Hojas disponibles: {xl.sheet_names}")
        
        for sheet_name in xl.sheet_names:
            print(f"\n--- Hoja: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Columnas: {list(df.columns)}")
            print(f"Total filas: {len(df)}")
            print("Primeras 3 filas:")
            print(df.head(3))
            print()
            
    except Exception as e:
        print(f"Error al leer DATOS EQUIPOS.xlsx: {e}")

def analizar_insumos():
    print("\n=== ANÁLISIS DE DATOS INSUMOS.xlsm ===")
    try:
        file_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm"
        
        # Leer el archivo Excel
        xl = pd.ExcelFile(file_path)
        print(f"Hojas disponibles: {xl.sheet_names}")
        
        for sheet_name in xl.sheet_names:
            print(f"\n--- Hoja: {sheet_name} ---")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"Columnas: {list(df.columns)}")
            print(f"Total filas: {len(df)}")
            print("Primeras 3 filas:")
            print(df.head(3))
            print()
            
    except Exception as e:
        print(f"Error al leer DATOS INSUMOS.xlsm: {e}")

if __name__ == "__main__":
    analizar_equipos()
    analizar_insumos()