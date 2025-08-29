#!/usr/bin/env python3
"""
Script para importar insumos desde archivos Excel al sistema de centralización
Autor: Sistema de Centralización de Laboratorios  
Fecha: 2025-08-29
"""

import os
import sys
import django
import pandas as pd
import time
from datetime import datetime, date
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio
from insumos.models import Insumo
from usuarios.models import Usuario

class ImportadorExcelInsumos:
    """Clase para importar insumos desde Excel"""
    
    def __init__(self, archivo_excel):
        self.archivo_excel = archivo_excel
        self.df = None
        self.errores = []
        self.exitosos = 0
        self.total_procesados = 0
        self.contador = 0  # Contador para códigos únicos
        
        # Mapeo de columnas Excel -> campos modelo
        self.mapeo_columnas = {
            'UNIDAD ACADÉMICA': 'unidad_academica',
            'LABORATORIO': 'laboratorio', 
            'CATEGORÍA': 'categoria',
            'NOMBRE DEL ELEMENTO': 'nombre_elemento',
            'DESCRIPCIÓN/CARACTERÍSTICAS': 'descripcion_caracteristicas',
            'MARCA / MODELO': 'marca_modelo',
            'CÓDIGO DE INVENTARIO (INTERNO)': 'codigo_inventario',
            'ESTADO': 'estado',
            'UBICACIÓN FÍSICA': 'ubicacion_fisica',
            'CANTIDAD': 'cantidad',
            'UNIDAD DE MEDIDA': 'unidad_medida',
            'FECHA DE INGRESO/COMPRA': 'fecha_ingreso_compra',
            'USO PRINCIPAL': 'uso_principal',
            'CARRERA': 'carrera',
            'SEMESTRE': 'semestre',
            'ASIGNATURA': 'asignatura',
            'UNIDAD TEMÁTICA': 'unidad_tematica',
            'CONDICIONES DE ALMACENAMIENTO': 'condiciones_almacenamiento',
            'OBSERVACIONES': 'observaciones',
            'INGRESE EL LINK DE LA FOTOGRAFIA DEL ELEMENTO': 'link_fotografia'
        }
        
        # Mapeo de valores para normalización
        self.mapeo_categorias = {
            'HERRAMIENTA': 'herramientas',
            'MATERIAL': 'materiales', 
            'REACTIVO': 'reactivos',
            'REACTIVOS': 'reactivos',
            'MATERIALES': 'materiales',
            'HERRAMIENTAS': 'herramientas'
        }
        
        self.mapeo_estados = {
            'OPERATIVO': 'bueno',
            'BUENO': 'bueno',
            'REGULAR': 'regular',
            'MALO': 'malo',
            'VENCIDO': 'vencido',
            'AGOTADO': 'agotado',
            'DESCARTADO': 'descartado'
        }
        
        self.mapeo_unidades = {
            'UNIDADES': 'unidades',
            'ML': 'ml',
            'LITROS': 'l',
            'L': 'l',
            'GRAMOS': 'g',
            'G': 'g',
            'KG': 'kg',
            'KILOGRAMOS': 'kg',
            'PIEZAS': 'piezas',
            'CAJAS': 'cajas',
            'FRASCOS': 'frascos'
        }
    
    def leer_archivo(self):
        """Leer archivo Excel"""
        try:
            print(f"📂 Leyendo archivo: {os.path.basename(self.archivo_excel)}")
            self.df = pd.read_excel(self.archivo_excel, engine='openpyxl')
            print(f"✅ Archivo leído: {len(self.df)} filas encontradas")
            return True
        except Exception as e:
            print(f"❌ Error al leer archivo: {e}")
            return False
    
    def generar_codigo_unico(self):
        """Genera un código de inventario único usando contador incremental"""
        self.contador += 1
        timestamp = int(time.time())
        return f"INS_{timestamp}_{self.contador:04d}"
    
    def normalizar_valor(self, valor, mapeo_dict):
        """Normalizar valores usando diccionario de mapeo"""
        if pd.isna(valor) or valor == "":
            return None
        
        valor_str = str(valor).strip().upper()
        return mapeo_dict.get(valor_str, valor_str.lower())
    
    def procesar_fecha(self, fecha):
        """Procesar fechas desde Excel"""
        if pd.isna(fecha):
            return None
        
        try:
            if isinstance(fecha, datetime):
                return fecha.date()
            elif isinstance(fecha, date):
                return fecha
            elif isinstance(fecha, str):
                # Intentar diferentes formatos
                for formato in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                    try:
                        return datetime.strptime(fecha, formato).date()
                    except:
                        continue
            return None
        except:
            return None
    
    def obtener_o_crear_unidad_academica(self, nombre):
        """Obtener o crear unidad académica"""
        if pd.isna(nombre) or not nombre:
            return None
        
        nombre = str(nombre).strip()
        unidad, created = UnidadAcademica.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Unidad académica {nombre}'}
        )
        return unidad
    
    def obtener_o_crear_laboratorio(self, nombre):
        """Obtener o crear laboratorio"""
        if pd.isna(nombre) or not nombre:
            # Usar laboratorio por defecto
            laboratorio, created = Laboratorio.objects.get_or_create(
                nombre='LAB_CIENCIAS_BASICAS',
                defaults={
                    'descripcion': 'Laboratorio de Ciencias Básicas',
                    'capacidad': 20,
                    'ubicacion': 'Por definir'
                }
            )
            return laboratorio
        
        # Mapear nombres comunes a nombres del modelo
        mapeo_laboratorios = {
            'PLANTA DE TRATAMIENTO DE AGUAS': 'LAB_QUIMICA',
            'ASFALTOS': 'LAB_CIVIL',
            'HORMIGONES': 'LAB_CIVIL', 
            'RESISTENCIA DE MATERIALES Y SUELOS': 'LAB_CIVIL',
            'LACTEOS': 'LAB_BIOTECNOLOGIA',
            'QUÍMICA': 'LAB_QUIMICA',
            'FÍSICA': 'LAB_FISICA_1',
            'SISTEMAS': 'LAB_SISTEMAS_1',
            'MECATRÓNICA': 'LAB_MECATRONICA',
            'INDUSTRIAL': 'LAB_INDUSTRIAL'
        }
        
        nombre = str(nombre).strip().upper()
        nombre_lab = mapeo_laboratorios.get(nombre, 'LAB_CIENCIAS_BASICAS')
        
        laboratorio, created = Laboratorio.objects.get_or_create(
            nombre=nombre_lab,
            defaults={
                'descripcion': f'Laboratorio {nombre}',
                'capacidad': 20,
                'ubicacion': 'Por definir'
            }
        )
        return laboratorio
    
    def obtener_o_crear_carrera(self, nombre, unidad_academica):
        """Obtener o crear carrera"""
        if pd.isna(nombre) or not nombre or not unidad_academica:
            # Crear carrera por defecto
            carrera, created = Carrera.objects.get_or_create(
                nombre="ING_CIVIL",
                unidad_academica=unidad_academica,
                defaults={
                    'descripcion': 'Ingeniería Civil'
                }
            )
            return carrera
        
        # Mapear nombres comunes a nombres del modelo
        mapeo_carreras = {
            'CIVIL': 'ING_CIVIL',
            'INGENIERÍA CIVIL': 'ING_CIVIL',
            'SISTEMAS': 'ING_SISTEMAS',
            'INGENIERÍA DE SISTEMAS': 'ING_SISTEMAS',
            'QUÍMICA': 'ING_AMBIENTAL',
            'INGENIERÍA QUÍMICA': 'ING_AMBIENTAL',
            'INDUSTRIAL': 'ING_INDUSTRIAL',
            'INGENIERÍA INDUSTRIAL': 'ING_INDUSTRIAL',
            'AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL',
            'INGENIERÍA AGROINDUSTRIAL': 'ING_AGROINDUSTRIAL'
        }
        
        nombre = str(nombre).strip().upper()
        nombre_carrera = mapeo_carreras.get(nombre, 'ING_CIVIL')
        
        carrera, created = Carrera.objects.get_or_create(
            nombre=nombre_carrera,
            unidad_academica=unidad_academica,
            defaults={
                'descripcion': f'Carrera {nombre}'
            }
        )
        return carrera
    
    def obtener_o_crear_asignatura(self, nombre, carrera, semestre=None):
        """Obtener o crear asignatura"""
        if pd.isna(nombre) or not nombre or not carrera:
            # Crear asignatura por defecto
            asignatura, created = Asignatura.objects.get_or_create(
                nombre="quimica_general",
                carrera=carrera,
                semestre=semestre if semestre else 1,
                defaults={
                    'carga_horaria_semanal': 4,
                    'carga_horaria_semestral': 80
                }
            )
            return asignatura
        
        # Mapear nombres comunes a nombres del modelo
        mapeo_asignaturas = {
            'QUÍMICA': 'quimica_general',
            'QUÍMICA GENERAL': 'quimica_general',
            'FÍSICA': 'fisica_i',
            'FÍSICA I': 'fisica_i',
            'MATEMÁTICA': 'matematica_i',
            'LABORATORIO': 'quimica_general',
            'PROCESOS': 'procesos_industriales',
            'MATERIALES': 'mecanica_materiales'
        }
        
        nombre = str(nombre).strip().upper()
        nombre_asignatura = mapeo_asignaturas.get(nombre, 'quimica_general')
        
        asignatura, created = Asignatura.objects.get_or_create(
            nombre=nombre_asignatura,
            carrera=carrera,
            semestre=semestre if semestre else 1,
            defaults={
                'carga_horaria_semanal': 4,
                'carga_horaria_semestral': 80
            }
        )
        return asignatura
    
    def obtener_o_crear_unidad_tematica(self, nombre, asignatura):
        """Obtener o crear unidad temática"""
        if pd.isna(nombre) or not nombre or not asignatura:
            # Crear unidad temática por defecto
            unidad_tematica, created = UnidadTematica.objects.get_or_create(
                nombre="Unidad General de Laboratorio",
                asignatura=asignatura,
                numero=1,
                defaults={
                    'descripcion': 'Unidad temática general para laboratorio'
                }
            )
            return unidad_tematica
        
        nombre = str(nombre).strip()
        unidad_tematica, created = UnidadTematica.objects.get_or_create(
            nombre=nombre,
            asignatura=asignatura,
            numero=1,  # Por defecto usar número 1
            defaults={
                'descripcion': f'Unidad temática: {nombre}'
            }
        )
        return unidad_tematica
    
    def procesar_insumo(self, fila):
        """Procesar una fila individual del Excel"""
        try:
            # 1. Unidad Académica
            nombre_unidad = fila.get('UNIDAD ACADÉMICA', '')
            unidad_academica = self.obtener_o_crear_unidad_academica(nombre_unidad)
            if not unidad_academica:
                raise ValueError("No se pudo crear/obtener la unidad académica")
            
            # 2. Laboratorio  
            nombre_lab = fila.get('LABORATORIO', '')
            laboratorio = self.obtener_o_crear_laboratorio(nombre_lab)
            if not laboratorio:
                raise ValueError("No se pudo crear/obtener el laboratorio")
            
            # 14. Carrera
            nombre_carrera = fila.get('CARRERA', '')
            semestre_raw = fila.get('SEMESTRE', 1)
            try:
                semestre = int(float(semestre_raw)) if not pd.isna(semestre_raw) else 1
            except:
                semestre = 1
            carrera = self.obtener_o_crear_carrera(nombre_carrera, unidad_academica)
            
            # 15. Asignatura 
            nombre_asignatura = fila.get('ASIGNATURA', '')
            asignatura = self.obtener_o_crear_asignatura(nombre_asignatura, carrera, semestre)
            
            # 16. Unidad Temática
            nombre_unidad_tematica = fila.get('UNIDAD TEMÁTICA', '')
            unidad_tematica = self.obtener_o_crear_unidad_tematica(nombre_unidad_tematica, asignatura)
            
            # Crear objeto Insumo
            insumo_data = {
                'unidad_academica': unidad_academica,
                'laboratorio': laboratorio,
                'carrera': carrera,
                'asignatura': asignatura,
                'unidad_tematica': unidad_tematica,
                
                # 3. Categoría
                'categoria': self.normalizar_valor(fila.get('CATEGORÍA', ''), self.mapeo_categorias) or 'materiales',
                
                # 4. Nombre del elemento
                'nombre_elemento': str(fila.get('NOMBRE DEL ELEMENTO', 'Sin nombre')).strip(),
                
                # 5. Descripción
                'descripcion_caracteristicas': str(fila.get('DESCRIPCIÓN/CARACTERÍSTICAS', '')).strip() or '-',
                
                # 6. Marca/Modelo
                'marca_modelo': str(fila.get('MARCA / MODELO', '')).strip() or '-',
                
                # 7. Código de inventario
                'codigo_inventario': self.generar_codigo_unico() if (pd.isna(fila.get('CÓDIGO DE INVENTARIO (INTERNO)', '')) or 
                                                                    str(fila.get('CÓDIGO DE INVENTARIO (INTERNO)', '')).strip() in ['', 'nan', 'NaN']) else str(fila.get('CÓDIGO DE INVENTARIO (INTERNO)', '')).strip(),
                
                # 8. Estado
                'estado': self.normalizar_valor(fila.get('ESTADO', ''), self.mapeo_estados) or 'bueno',
                
                # 9. Ubicación física
                'ubicacion_fisica': str(fila.get('UBICACIÓN FÍSICA', '')).strip() or '-',
                
                # 10. Cantidad
                'cantidad': float(fila.get('CANTIDAD', 0)) if not pd.isna(fila.get('CANTIDAD', 0)) else 0,
                
                # 11. Unidad de medida
                'unidad_medida': self.normalizar_valor(fila.get('UNIDAD DE MEDIDA', ''), self.mapeo_unidades) or 'unidades',
                
                # 12. Fecha de ingreso
                'fecha_ingreso_compra': self.procesar_fecha(fila.get('FECHA DE INGRESO/COMPRA')),
                
                # 13. Uso principal
                'uso_principal': 'practicas',  # Por defecto
                
                # 19. Condiciones de almacenamiento
                'condiciones_almacenamiento': 'temperatura_ambiente',  # Por defecto
                
                # 20. Observaciones
                'observaciones': str(fila.get('OBSERVACIONES', '')).strip() or '-',
                
                # 21. Link fotografía
                'link_fotografia': str(fila.get('INGRESE EL LINK DE LA FOTOGRAFIA DEL ELEMENTO', '')).strip() or ''
            }
            
            # Crear el insumo
            insumo = Insumo.objects.create(**insumo_data)
            
            print(f"✅ {self.exitosos + 1}: {insumo.nombre_elemento} | {unidad_academica.nombre} - {laboratorio.nombre}")
            return True
            
        except Exception as e:
            error_msg = f"Error en fila {self.total_procesados + 1}: {e}"
            self.errores.append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def importar(self):
        """Proceso principal de importación"""
        if not self.leer_archivo():
            return False
        
        print("\n🚀 INICIANDO IMPORTACIÓN DE INSUMOS")
        print("=" * 60)
        
        # Confirmar importación
        respuesta = input(f"¿Desea importar {len(self.df)} insumos? (s/N): ").lower()
        if respuesta != 's':
            print("❌ Importación cancelada")
            return False
        
        print(f"\n📦 Procesando {len(self.df)} insumos...")
        print("-" * 60)
        
        for index, fila in self.df.iterrows():
            self.total_procesados += 1
            
            if self.procesar_insumo(fila):
                self.exitosos += 1
        
        # Mostrar resumen
        self.mostrar_resumen()
        return True
    
    def mostrar_resumen(self):
        """Mostrar resumen de la importación"""
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE IMPORTACIÓN")
        print("=" * 60)
        print(f"✅ Insumos importados exitosamente: {self.exitosos}")
        print(f"❌ Errores encontrados: {len(self.errores)}")
        print(f"📋 Total procesados: {self.total_procesados}")
        
        if self.errores:
            print(f"\n❌ ERRORES ENCONTRADOS:")
            for error in self.errores[:10]:  # Mostrar solo los primeros 10
                print(f"   - {error}")
            if len(self.errores) > 10:
                print(f"   ... y {len(self.errores) - 10} errores más")
        
        if self.exitosos > 0:
            print(f"\n🎉 Los {self.exitosos} insumos ya están disponibles en:")
            print("   📍 http://127.0.0.1:8000/insumos/ (Lista completa)")
            print("   📍 Dashboard principal para estadísticas")

def main():
    """Función principal"""
    if len(sys.argv) != 2:
        print("❌ Uso: python importar_excel_insumos.py <archivo_excel>")
        print("📋 Ejemplo: python importar_excel_insumos.py datos_insumos.xlsx")
        sys.exit(1)
    
    archivo_excel = sys.argv[1]
    
    if not os.path.exists(archivo_excel):
        print(f"❌ El archivo no existe: {archivo_excel}")
        sys.exit(1)
    
    # Crear importador y ejecutar
    importador = ImportadorExcelInsumos(archivo_excel)
    
    if importador.importar():
        print("\n🎉 ¡Importación completada! Insumos disponibles en el sistema")
    else:
        print("\n❌ La importación falló")
        sys.exit(1)

if __name__ == "__main__":
    main()
