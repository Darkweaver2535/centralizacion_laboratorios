#!/usr/bin/env python3
"""
Script para analizar archivos Excel de insumos antes de la importación
Autor: Sistema de Centralización de Laboratorios
Fecha: 2025-08-29
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

class ExtractorExcelInsumos:
    """Clase para extraer y analizar datos de Excel de insumos"""
    
    def __init__(self, archivo_excel):
        self.archivo_excel = archivo_excel
        self.df = None
        
    def leer_archivo(self):
        """Leer archivo Excel con diferentes motores"""
        print(f"📁 Analizando archivo: {self.archivo_excel}")
        print("=" * 80)
        
        try:
            # Intentar con openpyxl (para .xlsx y .xlsm)
            self.df = pd.read_excel(self.archivo_excel, engine='openpyxl')
            print("✅ Archivo leído exitosamente con openpyxl")
        except Exception as e1:
            try:
                # Intentar con xlrd
                self.df = pd.read_excel(self.archivo_excel, engine='xlrd')
                print("✅ Archivo leído exitosamente con xlrd")
            except Exception as e2:
                try:
                    # Intentar sin especificar motor
                    self.df = pd.read_excel(self.archivo_excel)
                    print("✅ Archivo leído exitosamente")
                except Exception as e3:
                    print(f"❌ Error al leer archivo: {e3}")
                    return False
        
        return True
    
    def analizar_estructura(self):
        """Analizar la estructura del archivo"""
        if self.df is None:
            print("❌ No hay datos para analizar")
            return
        
        print(f"📊 Total de filas: {len(self.df)}")
        print(f"📋 Total de columnas: {len(self.df.columns)}")
        print()
        
        print("📝 COLUMNAS ENCONTRADAS:")
        print("-" * 50)
        for i, col in enumerate(self.df.columns, 1):
            print(f"{i:2d}. {col}")
        
        print()
        print("🔍 DISTRIBUCIÓN DE DATOS:")
        print("-" * 30)
        
        # Contar valores no nulos por columna
        for col in self.df.columns:
            no_nulos = self.df[col].notna().sum()
            porcentaje = (no_nulos / len(self.df)) * 100
            print(f"  {col[:30]:<30}: {no_nulos:4d}/{len(self.df)} ({porcentaje:.1f}%)")
    
    def mostrar_muestras(self, num_filas=3):
        """Mostrar las primeras filas como muestra"""
        if self.df is None:
            return
        
        print()
        print(f"🔍 PRIMERAS {num_filas} FILAS DE MUESTRA:")
        print("=" * 80)
        
        for idx in range(min(num_filas, len(self.df))):
            print(f"📦 INSUMO {idx + 1}:")
            print("-" * 40)
            
            for col in self.df.columns:
                valor = self.df.iloc[idx][col]
                if pd.isna(valor):
                    valor = "N/A"
                elif isinstance(valor, str):
                    valor = valor.strip()
                
                # Truncar valores muy largos
                if len(str(valor)) > 60:
                    valor = str(valor)[:57] + "..."
                
                print(f"  {col}: {valor}")
            print()
    
    def analizar_campos_especificos(self):
        """Analizar campos específicos importantes"""
        if self.df is None:
            return
        
        print("🎯 ANÁLISIS DE CAMPOS ESPECÍFICOS:")
        print("=" * 50)
        
        # Mapeo esperado de columnas
        columnas_esperadas = [
            'UNIDAD ACADÉMICA',
            'LABORATORIO', 
            'CATEGORÍA',
            'NOMBRE DEL ELEMENTO',
            'DESCRIPCIÓN/CARACTERÍSTICAS',
            'MARCA / MODELO',
            'CÓDIGO DE INVENTARIO (INTERNO)',
            'ESTADO',
            'UBICACIÓN FÍSICA',
            'CANTIDAD',
            'UNIDAD DE MEDIDA',
            'FECHA DE INGRESO/COMPRA',
            'USO PRINCIPAL',
            'CARRERA',
            'SEMESTRE',
            'ASIGNATURA',
            'UNIDAD TEMÁTICA',
            'CONDICIONES DE ALMACENAMIENTO',
            'OBSERVACIONES',
            'INGRESE EL LINK DE LA FOTOGRAFIA DEL ELEMENTO'
        ]
        
        print("📋 Columnas esperadas vs encontradas:")
        for col_esperada in columnas_esperadas:
            encontrada = col_esperada in self.df.columns
            estado = "✅" if encontrada else "❌"
            print(f"  {estado} {col_esperada}")
        
        print()
        
        # Analizar valores únicos en campos importantes
        campos_analizar = ['UNIDAD ACADÉMICA', 'LABORATORIO', 'CATEGORÍA', 'ESTADO']
        
        for campo in campos_analizar:
            if campo in self.df.columns:
                valores_unicos = self.df[campo].dropna().unique()
                print(f"🔸 {campo}: {len(valores_unicos)} valores únicos")
                for i, valor in enumerate(valores_unicos[:5]):  # Mostrar solo los primeros 5
                    print(f"    {i+1}. {valor}")
                if len(valores_unicos) > 5:
                    print(f"    ... y {len(valores_unicos)-5} más")
                print()
    
    def generar_resumen(self):
        """Generar resumen completo del análisis"""
        if self.df is None:
            return
        
        print("📊 RESUMEN DEL ANÁLISIS:")
        print("=" * 50)
        print(f"📁 Archivo: {os.path.basename(self.archivo_excel)}")
        print(f"📦 Total insumos: {len(self.df)}")
        print(f"📋 Total columnas: {len(self.df.columns)}")
        print(f"⏰ Fecha análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar si está listo para importación
        columnas_criticas = ['NOMBRE DEL ELEMENTO', 'CANTIDAD']
        listo_importacion = all(col in self.df.columns for col in columnas_criticas)
        
        print(f"🚀 Listo para importación: {'✅ SÍ' if listo_importacion else '❌ NO'}")
        
        if listo_importacion:
            print()
            print("🎯 SIGUIENTE PASO:")
            print("   Ejecutar: python importar_excel_insumos.py [archivo]")

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("❌ Uso: python extraer_excel_insumos.py <archivo_excel>")
        sys.exit(1)
    
    archivo_excel = sys.argv[1]
    
    if not os.path.exists(archivo_excel):
        print(f"❌ El archivo no existe: {archivo_excel}")
        sys.exit(1)
    
    # Crear extractor y analizar
    extractor = ExtractorExcelInsumos(archivo_excel)
    
    if extractor.leer_archivo():
        extractor.analizar_estructura()
        extractor.mostrar_muestras()
        extractor.analizar_campos_especificos()
        extractor.generar_resumen()
    else:
        print("❌ No se pudo analizar el archivo")
        sys.exit(1)

if __name__ == "__main__":
    main()
