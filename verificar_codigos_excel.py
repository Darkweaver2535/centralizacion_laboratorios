#!/usr/bin/env python3
"""
Script para verificar códigos de inventario en Excel
"""

import pandas as pd
from collections import Counter

# Leer archivo Excel
archivo = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/RECOPILACION DE DATOS materiales_19_08_2025_UUAA (1).xlsm"
print(f"📂 Leyendo archivo: {archivo}")

try:
    df = pd.read_excel(archivo, engine='openpyxl')
    print(f"✅ Archivo leído: {len(df)} filas")
    
    # Verificar columna de códigos
    if 'CÓDIGO DE INVENTARIO (INTERNO)' in df.columns:
        codigos = df['CÓDIGO DE INVENTARIO (INTERNO)'].tolist()
        
        # Contar valores
        print(f"\n📊 ANÁLISIS DE CÓDIGOS DE INVENTARIO:")
        print(f"Total códigos: {len(codigos)}")
        
        # Contar valores únicos
        codigos_no_nulos = [c for c in codigos if pd.notna(c) and c != ""]
        print(f"Códigos no vacíos: {len(codigos_no_nulos)}")
        
        # Buscar duplicados
        contador = Counter(codigos_no_nulos)
        duplicados = {k: v for k, v in contador.items() if v > 1}
        
        if duplicados:
            print(f"\n❌ CÓDIGOS DUPLICADOS ENCONTRADOS:")
            for codigo, cantidad in duplicados.items():
                print(f"  '{codigo}': {cantidad} veces")
        else:
            print(f"\n✅ No hay códigos duplicados")
            
        # Mostrar algunos ejemplos
        print(f"\n📋 PRIMEROS 10 CÓDIGOS:")
        for i, codigo in enumerate(codigos[:10], 1):
            print(f"  {i}: '{codigo}'")
            
    else:
        print("❌ Columna 'CÓDIGO DE INVENTARIO (INTERNO)' no encontrada")
        print("Columnas disponibles:", list(df.columns))
        
except Exception as e:
    print(f"❌ Error: {e}")
