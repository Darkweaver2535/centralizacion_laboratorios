#!/usr/bin/env python3
"""
Script simple para extraer y analizar datos de un archivo Excel de equipos
Columnas: N, UNIDAD ACADEMICA, RESPONSABLE, C.I., CARGO, OFICINA, CODIGO, DESCRIPCION DEL ACTIVO, ESTADO, FECHA DE ASIGNACION

Este script solo extrae y muestra los datos sin modificar la base de datos.
"""

import pandas as pd
import sys
from datetime import datetime
from pathlib import Path

class ExtractorExcel:
    """Clase para extraer y analizar datos de Excel sin modificar BD"""
    
    def __init__(self, archivo_excel):
        self.archivo_excel = archivo_excel
        self.df = None
    
    def cargar_archivo(self):
        """Cargar y validar el archivo Excel"""
        try:
            if not Path(self.archivo_excel).exists():
                raise FileNotFoundError(f"Archivo no encontrado: {self.archivo_excel}")
            
            # Leer Excel
            self.df = pd.read_excel(self.archivo_excel)
            
            print(f"✅ Archivo cargado: {len(self.df)} filas, {len(self.df.columns)} columnas")
            print(f"📋 Columnas encontradas: {list(self.df.columns)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al cargar archivo: {e}")
            return False
    
    def limpiar_datos(self):
        """Limpiar y preparar datos para análisis"""
        if self.df is None:
            return False
        
        try:
            # Limpiar espacios y valores nulos
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].astype(str).str.strip()
                    self.df[col] = self.df[col].replace('nan', '')
            
            # Procesar fechas si existe la columna
            if 'FECHA DE ASIGNACION' in self.df.columns:
                self.df['FECHA DE ASIGNACION'] = pd.to_datetime(
                    self.df['FECHA DE ASIGNACION'], 
                    errors='coerce'
                )
            
            print("✅ Datos limpiados correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al limpiar datos: {e}")
            return False
    
    def analizar_datos(self):
        """Realizar análisis estadístico de los datos"""
        if self.df is None:
            return
        
        print("\n" + "="*60)
        print("📊 ANÁLISIS DE DATOS")
        print("="*60)
        
        # Información general
        print(f"📈 Total de registros: {len(self.df)}")
        print(f"📈 Registros con datos completos: {len(self.df.dropna())}")
        
        # Análisis por unidad académica
        if 'UNIDAD ACADEMICA' in self.df.columns:
            print(f"\n🏢 DISTRIBUCIÓN POR UNIDAD ACADÉMICA:")
            unidades = self.df['UNIDAD ACADEMICA'].value_counts()
            for unidad, cantidad in unidades.items():
                print(f"   {unidad}: {cantidad} equipos")
        
        # Análisis por estado
        if 'ESTADO' in self.df.columns:
            print(f"\n🔧 DISTRIBUCIÓN POR ESTADO:")
            estados = self.df['ESTADO'].value_counts()
            for estado, cantidad in estados.items():
                print(f"   {estado}: {cantidad} equipos")
        
        # Análisis por responsable
        if 'RESPONSABLE' in self.df.columns:
            responsables_unicos = self.df['RESPONSABLE'].nunique()
            print(f"\n👥 RESPONSABLES ÚNICOS: {responsables_unicos}")
            
            # Top 10 responsables con más equipos
            top_responsables = self.df['RESPONSABLE'].value_counts().head(10)
            print(f"   Top 10 responsables:")
            for responsable, cantidad in top_responsables.items():
                print(f"   - {responsable}: {cantidad} equipos")
        
        # Análisis de códigos
        if 'CODIGO' in self.df.columns:
            codigos_vacios = self.df['CODIGO'].isna().sum() + (self.df['CODIGO'] == '').sum()
            print(f"\n🔢 CÓDIGOS:")
            print(f"   Equipos sin código: {codigos_vacios}")
            print(f"   Equipos con código: {len(self.df) - codigos_vacios}")
        
        # Análisis de fechas
        if 'FECHA DE ASIGNACION' in self.df.columns:
            fechas_validas = self.df['FECHA DE ASIGNACION'].notna().sum()
            print(f"\n📅 FECHAS DE ASIGNACIÓN:")
            print(f"   Fechas válidas: {fechas_validas}")
            print(f"   Fechas faltantes: {len(self.df) - fechas_validas}")
            
            if fechas_validas > 0:
                fecha_min = self.df['FECHA DE ASIGNACION'].min()
                fecha_max = self.df['FECHA DE ASIGNACION'].max()
                print(f"   Rango: {fecha_min.strftime('%Y-%m-%d')} a {fecha_max.strftime('%Y-%m-%d')}")
    
    def mostrar_muestra(self, n=10):
        """Mostrar una muestra de los datos"""
        if self.df is None:
            return
        
        print(f"\n" + "="*60)
        print(f"🔍 MUESTRA DE DATOS (primeros {n} registros)")
        print("="*60)
        
        # Mostrar columnas principales
        columnas_mostrar = []
        for col in ['N', 'UNIDAD ACADEMICA', 'RESPONSABLE', 'DESCRIPCION DEL ACTIVO', 'ESTADO']:
            if col in self.df.columns:
                columnas_mostrar.append(col)
        
        if columnas_mostrar:
            muestra = self.df[columnas_mostrar].head(n)
            print(muestra.to_string(index=False, max_colwidth=30))
        else:
            print(self.df.head(n).to_string(index=False, max_colwidth=30))
    
    def exportar_resumen(self, archivo_salida=None):
        """Exportar resumen de datos a un archivo"""
        if self.df is None:
            return False
        
        if archivo_salida is None:
            archivo_salida = f"resumen_equipos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                f.write("RESUMEN DE ANÁLISIS DE EQUIPOS\n")
                f.write("="*50 + "\n\n")
                f.write(f"Archivo analizado: {self.archivo_excel}\n")
                f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de registros: {len(self.df)}\n\n")
                
                # Resumen por unidad académica
                if 'UNIDAD ACADEMICA' in self.df.columns:
                    f.write("DISTRIBUCIÓN POR UNIDAD ACADÉMICA:\n")
                    unidades = self.df['UNIDAD ACADEMICA'].value_counts()
                    for unidad, cantidad in unidades.items():
                        f.write(f"  {unidad}: {cantidad}\n")
                    f.write("\n")
                
                # Resumen por estado
                if 'ESTADO' in self.df.columns:
                    f.write("DISTRIBUCIÓN POR ESTADO:\n")
                    estados = self.df['ESTADO'].value_counts()
                    for estado, cantidad in estados.items():
                        f.write(f"  {estado}: {cantidad}\n")
                    f.write("\n")
                
                # Lista completa de equipos
                f.write("LISTA COMPLETA DE EQUIPOS:\n")
                f.write("-" * 50 + "\n")
                
                for index, fila in self.df.iterrows():
                    f.write(f"\nN°: {fila.get('N', 'N/A')}\n")
                    f.write(f"Unidad: {fila.get('UNIDAD ACADEMICA', 'N/A')}\n")
                    f.write(f"Responsable: {fila.get('RESPONSABLE', 'N/A')}\n")
                    f.write(f"C.I.: {fila.get('C.I.', 'N/A')}\n")
                    f.write(f"Cargo: {fila.get('CARGO', 'N/A')}\n")
                    f.write(f"Oficina: {fila.get('OFICINA', 'N/A')}\n")
                    f.write(f"Código: {fila.get('CODIGO', 'N/A')}\n")
                    f.write(f"Descripción: {fila.get('DESCRIPCION DEL ACTIVO', 'N/A')}\n")
                    f.write(f"Estado: {fila.get('ESTADO', 'N/A')}\n")
                    f.write(f"Fecha: {fila.get('FECHA DE ASIGNACION', 'N/A')}\n")
                    f.write("-" * 30 + "\n")
            
            print(f"✅ Resumen exportado a: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"❌ Error al exportar resumen: {e}")
            return False
    
    def extraer_datos_json(self):
        """Extraer datos en formato JSON para integración"""
        if self.df is None:
            return None
        
        try:
            # Convertir DataFrame a lista de diccionarios
            datos = []
            for index, fila in self.df.iterrows():
                item = {
                    'numero': fila.get('N', ''),
                    'unidad_academica': fila.get('UNIDAD ACADEMICA', ''),
                    'responsable': fila.get('RESPONSABLE', ''),
                    'ci': fila.get('C.I.', ''),
                    'cargo': fila.get('CARGO', ''),
                    'oficina': fila.get('OFICINA', ''),
                    'codigo': fila.get('CODIGO', ''),
                    'descripcion': fila.get('DESCRIPCION DEL ACTIVO', ''),
                    'estado': fila.get('ESTADO', ''),
                    'fecha_asignacion': str(fila.get('FECHA DE ASIGNACION', ''))
                }
                datos.append(item)
            
            return datos
            
        except Exception as e:
            print(f"❌ Error al extraer datos JSON: {e}")
            return None

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python extraer_excel_equipos.py <archivo_excel>")
        print("Ejemplo: python extraer_excel_equipos.py equipos.xlsx")
        return 1
    
    archivo_excel = sys.argv[1]
    
    # Crear extractor
    extractor = ExtractorExcel(archivo_excel)
    
    # Cargar archivo
    if not extractor.cargar_archivo():
        return 1
    
    # Limpiar datos
    if not extractor.limpiar_datos():
        return 1
    
    # Mostrar muestra
    extractor.mostrar_muestra(5)
    
    # Realizar análisis
    extractor.analizar_datos()
    
    # Preguntar si exportar resumen
    respuesta = input("\n¿Desea exportar un resumen completo a archivo? (s/N): ")
    if respuesta.lower() == 's':
        extractor.exportar_resumen()
    
    # Preguntar si mostrar datos JSON
    respuesta = input("¿Desea ver los datos en formato JSON? (s/N): ")
    if respuesta.lower() == 's':
        import json
        datos_json = extractor.extraer_datos_json()
        if datos_json:
            print("\n📋 DATOS EN FORMATO JSON:")
            print(json.dumps(datos_json[:3], indent=2, ensure_ascii=False))
            print(f"... (mostrando solo los primeros 3 de {len(datos_json)} registros)")
    
    print("\n🎉 Análisis completado exitosamente!")
    return 0

if __name__ == "__main__":
    exit(main())
