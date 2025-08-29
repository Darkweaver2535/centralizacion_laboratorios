#!/usr/bin/env python3
"""
Script para importar datos de equipos desde un archivo Excel
Columnas del Excel: N, UNIDAD ACADEMICA, RESPONSABLE, C.I., CARGO, OFICINA, CODIGO, DESCRIPCION DEL ACTIVO, ESTADO, FECHA DE ASIGNACION

Autor: Sistema de Centralización de Laboratorios
Fecha: 2024
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.db import transaction
from core.models import UnidadAcademica, Laboratorio
from usuarios.models import Usuario
from equipos.models import Equipo

class ImportadorExcel:
    """Clase para importar datos de equipos desde Excel"""
    
    def __init__(self, archivo_excel):
        """
        Inicializar el importador
        
        Args:
            archivo_excel (str): Ruta al archivo Excel
        """
        self.archivo_excel = archivo_excel
        self.df = None
        self.errores = []
        self.exitosos = []
        
        # Mapeo de estados del Excel a estados del sistema
        self.mapeo_estados = {
            'OPERATIVO': 'operativo',
            'OPERATIVO.': 'operativo',
            'BUENO': 'operativo',
            'REGULAR': 'necesita_mantenimiento',
            'MALO': 'fuera_servicio',
            'FUERA DE SERVICIO': 'fuera_servicio',
            'EN MANTENIMIENTO': 'necesita_mantenimiento',
            'DAÑADO': 'fuera_servicio',
            'OBSOLETO': 'obsoleto',
            'NECESITA MANTENIMIENTO': 'necesita_mantenimiento',
        }
        
        # Mapeo de unidades académicas del Excel al sistema
        self.mapeo_unidades = {
            'UALP': 'UALP',
            'LA PAZ': 'UALP',
            'UACB': 'UACB', 
            'COCHABAMBA': 'UACB',
            'UASC': 'UASC',
            'SANTA CRUZ': 'UASC',
            'UATP': 'UATP',
            'TROPICO': 'UATP',
            'UCRB': 'UCRB',
            'RIBERALTA': 'UCRB',
        }
    
    def validar_archivo(self):
        """Validar que el archivo Excel existe y tiene el formato correcto"""
        try:
            if not os.path.exists(self.archivo_excel):
                raise FileNotFoundError(f"El archivo {self.archivo_excel} no existe")
            
            # Leer el archivo Excel
            self.df = pd.read_excel(self.archivo_excel)
            
            # Verificar columnas requeridas
            columnas_requeridas = [
                'N', 'UNIDAD ACADEMICA', 'RESPONSABLE', 'C.I.', 
                'CARGO', 'OFICINA', 'CODIGO', 'DESCRIPCION DEL ACTIVO', 
                'ESTADO', 'FECHA DE ASIGNACION'
            ]
            
            columnas_faltantes = []
            for col in columnas_requeridas:
                if col not in self.df.columns:
                    columnas_faltantes.append(col)
            
            if columnas_faltantes:
                raise ValueError(f"Faltan las siguientes columnas: {', '.join(columnas_faltantes)}")
            
            print(f"✅ Archivo validado correctamente: {len(self.df)} filas encontradas")
            return True
            
        except Exception as e:
            print(f"❌ Error al validar el archivo: {str(e)}")
            return False
    
    def limpiar_datos(self):
        """Limpiar y normalizar los datos del Excel"""
        try:
            # Limpiar valores nulos y espacios
            self.df = self.df.fillna('')
            
            # Normalizar columnas de texto
            columnas_texto = ['UNIDAD ACADEMICA', 'RESPONSABLE', 'CARGO', 'OFICINA', 
                            'CODIGO', 'DESCRIPCION DEL ACTIVO', 'ESTADO']
            
            for col in columnas_texto:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.strip().str.upper()
            
            # Limpiar C.I.
            if 'C.I.' in self.df.columns:
                self.df['C.I.'] = self.df['C.I.'].astype(str).str.replace(r'\D', '', regex=True)
            
            # Procesar fechas
            if 'FECHA DE ASIGNACION' in self.df.columns:
                self.df['FECHA DE ASIGNACION'] = pd.to_datetime(
                    self.df['FECHA DE ASIGNACION'], 
                    errors='coerce'
                )
            
            print("✅ Datos limpiados correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error al limpiar datos: {str(e)}")
            return False
    
    def obtener_unidad_academica(self, nombre_unidad):
        """Obtener objeto UnidadAcademica basado en el nombre del Excel"""
        try:
            nombre_normalizado = str(nombre_unidad).strip().upper()
            
            # Buscar en el mapeo
            codigo_unidad = self.mapeo_unidades.get(nombre_normalizado)
            
            if not codigo_unidad:
                # Intentar coincidencia parcial
                for excel_name, db_code in self.mapeo_unidades.items():
                    if excel_name in nombre_normalizado or nombre_normalizado in excel_name:
                        codigo_unidad = db_code
                        break
            
            if codigo_unidad:
                return UnidadAcademica.objects.get(nombre=codigo_unidad)
            else:
                raise ValueError(f"Unidad académica no encontrada: {nombre_unidad}")
                
        except UnidadAcademica.DoesNotExist:
            raise ValueError(f"Unidad académica no existe en BD: {codigo_unidad}")
    
    def obtener_estado_normalizado(self, estado_excel):
        """Normalizar estado del Excel al formato del sistema"""
        estado_normalizado = str(estado_excel).strip().upper()
        return self.mapeo_estados.get(estado_normalizado, 'operativo')
    
    def obtener_o_crear_usuario_responsable(self, nombre, ci, cargo, oficina, unidad_academica):
        """Obtener o crear usuario responsable basado en los datos del Excel"""
        try:
            # Primero intentar buscar por C.I.
            if ci and len(str(ci).strip()) >= 6:
                ci_limpio = str(ci).strip()
                try:
                    usuario = Usuario.objects.get(numero_documento=ci_limpio)
                    return usuario
                except Usuario.DoesNotExist:
                    pass
            
            # Si no existe, crear nuevo usuario
            if nombre and nombre.strip():
                # Generar username único
                nombre_base = nombre.replace(' ', '').lower()[:10]
                username = nombre_base
                contador = 1
                
                while Usuario.objects.filter(username=username).exists():
                    username = f"{nombre_base}{contador}"
                    contador += 1
                
                # Generar correo institucional temporal
                correo_temporal = f"{username}@temp.emi.edu.bo"
                
                # Crear usuario
                usuario = Usuario.objects.create_user(
                    username=username,
                    correo_institucional=correo_temporal,
                    email=correo_temporal,
                    first_name=nombre.title(),
                    numero_documento=str(ci).strip() if ci else '',
                    rol='auxiliar',
                    unidad_academica=unidad_academica,
                    cargo=cargo.title() if cargo else 'Responsable de Equipo',
                    oficina=oficina.title() if oficina else '',
                    estado_usuario='activo',
                    debe_cambiar_password=True
                )
                
                print(f"✅ Usuario creado: {username} - {nombre}")
                return usuario
            else:
                raise ValueError("Nombre de responsable no proporcionado")
                
        except Exception as e:
            raise ValueError(f"Error al crear usuario responsable: {str(e)}")
    
    def obtener_laboratorio_default(self, unidad_academica):
        """Obtener laboratorio por defecto para la unidad académica"""
        try:
            # Buscar laboratorio general o crear uno por defecto
            laboratorio = Laboratorio.objects.filter(
                unidad_academica=unidad_academica,
                nombre__icontains='general'
            ).first()
            
            if not laboratorio:
                # Crear laboratorio por defecto
                laboratorio = Laboratorio.objects.create(
                    unidad_academica=unidad_academica,
                    nombre=f"Laboratorio General {unidad_academica.get_nombre_display()}",
                    descripcion="Laboratorio creado automáticamente durante importación de equipos",
                    capacidad_estudiantes=30,
                    area_m2=50.0,
                    tiene_agua=True,
                    tiene_electricidad=True,
                    tiene_gas=False,
                    tiene_ventilacion=True,
                    ubicacion_piso=1,
                    ubicacion_edificio="Principal"
                )
                print(f"✅ Laboratorio creado: {laboratorio.nombre}")
            
            return laboratorio
            
        except Exception as e:
            raise ValueError(f"Error al obtener laboratorio: {str(e)}")
    
    def procesar_fila(self, fila):
        """Procesar una fila individual del Excel"""
        try:
            # Extraer datos de la fila
            numero = fila.get('N', '')
            unidad_academica_str = fila.get('UNIDAD ACADEMICA', '')
            responsable = fila.get('RESPONSABLE', '')
            ci = fila.get('C.I.', '')
            cargo = fila.get('CARGO', '')
            oficina = fila.get('OFICINA', '')
            codigo = fila.get('CODIGO', '')
            descripcion = fila.get('DESCRIPCION DEL ACTIVO', '')
            estado_str = fila.get('ESTADO', '')
            fecha_asignacion = fila.get('FECHA DE ASIGNACION', None)
            
            # Validaciones básicas
            if not descripcion or descripcion.strip() == '':
                raise ValueError("Descripción del activo es requerida")
            
            if not unidad_academica_str or unidad_academica_str.strip() == '':
                raise ValueError("Unidad académica es requerida")
            
            # Obtener objetos relacionados
            unidad_academica = self.obtener_unidad_academica(unidad_academica_str)
            estado_normalizado = self.obtener_estado_normalizado(estado_str)
            usuario_responsable = self.obtener_o_crear_usuario_responsable(
                responsable, ci, cargo, oficina, unidad_academica
            )
            laboratorio = self.obtener_laboratorio_default(unidad_academica)
            
            # Crear código de inventario si no existe
            codigo_inventario = codigo.strip() if codigo else None
            if not codigo_inventario:
                # Generar código automático basado en patrón
                contador = Equipo.objects.count() + 1
                codigo_inventario = f"{unidad_academica.nombre}-EQ-{contador:06d}"
            
            # Verificar si ya existe un equipo con este código
            if Equipo.objects.filter(codigo_inventario=codigo_inventario).exists():
                # Modificar código para hacerlo único
                base_codigo = codigo_inventario
                contador = 1
                while Equipo.objects.filter(codigo_inventario=codigo_inventario).exists():
                    codigo_inventario = f"{base_codigo}-{contador}"
                    contador += 1
            
            # Crear registro de equipo
            # Nota: Necesitamos datos mínimos requeridos que no están en el Excel
            # Los crearemos con valores por defecto
            
            # Para este script, crearemos un equipo simplificado que contenga
            # la información del Excel como observaciones y datos básicos
            
            equipo_data = {
                'unidad_academica': unidad_academica,
                'codigo_inventario': codigo_inventario,
                'equipo_existente': descripcion[:200],  # Limitar longitud
                'estado': estado_normalizado,
                'numero_unidades': 1,
                'es_activo_fijo': True,
                'laboratorio': laboratorio,
                'usuario_creador': usuario_responsable,
                'observaciones': f"""
Datos importados desde Excel:
- N°: {numero}
- Responsable: {responsable}
- C.I.: {ci}
- Cargo: {cargo}
- Oficina: {oficina}
- Código original: {codigo}
- Estado original: {estado_str}
- Fecha asignación: {fecha_asignacion}
                """.strip()
            }
            
            # Para los campos requeridos que no tenemos del Excel,
            # usaremos valores por defecto temporales
            from core.models import Carrera, Asignatura
            from guias.models import UnidadTematica, GuiaLaboratorio, Practica
            
            # Obtener o crear datos por defecto
            carrera_default = Carrera.objects.filter(unidad_academica=unidad_academica).first()
            if not carrera_default:
                raise ValueError(f"No hay carreras configuradas para {unidad_academica}")
            
            asignatura_default = Asignatura.objects.first()
            if not asignatura_default:
                raise ValueError("No hay asignaturas configuradas en el sistema")
            
            # Para las guías, necesitamos crearlas dinámicamente o usar valores por defecto
            unidad_tematica_default, _ = UnidadTematica.objects.get_or_create(
                nombre="Equipos Importados",
                defaults={
                    'descripcion': 'Unidad temática para equipos importados desde Excel',
                    'numero_tema': 1,
                    'horas_academicas': 2
                }
            )
            
            guia_default, _ = GuiaLaboratorio.objects.get_or_create(
                titulo="Guía de Equipos Importados",
                defaults={
                    'unidad_tematica': unidad_tematica_default,
                    'numero_guia': 1,
                    'duracion_horas': 2,
                    'tipo_practica': 'verificacion',
                    'modalidad': 'presencial'
                }
            )
            
            practica_default, _ = Practica.objects.get_or_create(
                nombre="Uso de Equipos Importados",
                defaults={
                    'guia_laboratorio': guia_default,
                    'numero_practica': 1,
                    'duracion_minutos': 120,
                    'descripcion': 'Práctica para equipos importados desde Excel'
                }
            )
            
            # Agregar campos requeridos con valores por defecto
            equipo_data.update({
                'carrera': carrera_default,
                'semestre': 1,  # Valor por defecto
                'asignatura': asignatura_default,
                'carga_horaria_semanal': 2,
                'carga_horaria_semestral': 32,
                'unidad_tematica': unidad_tematica_default,
                'guia_laboratorio': guia_default,
                'practica': practica_default,
            })
            
            # Crear el equipo
            equipo = Equipo.objects.create(**equipo_data)
            
            return {
                'exito': True,
                'equipo': equipo,
                'codigo': codigo_inventario,
                'descripcion': descripcion,
                'responsable': responsable
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'fila': numero,
                'descripcion': descripcion if 'descripcion' in locals() else 'N/A'
            }
    
    def importar_datos(self):
        """Importar todos los datos del Excel"""
        print(f"\n🚀 Iniciando importación de {len(self.df)} equipos...")
        
        with transaction.atomic():
            for index, fila in self.df.iterrows():
                resultado = self.procesar_fila(fila)
                
                if resultado['exito']:
                    self.exitosos.append(resultado)
                    print(f"✅ Fila {index + 1}: {resultado['descripcion'][:50]}...")
                else:
                    self.errores.append(resultado)
                    print(f"❌ Fila {index + 1}: {resultado['error']}")
        
        # Resumen final
        print(f"\n📊 RESUMEN DE IMPORTACIÓN:")
        print(f"   ✅ Exitosos: {len(self.exitosos)}")
        print(f"   ❌ Errores: {len(self.errores)}")
        print(f"   📋 Total procesados: {len(self.exitosos) + len(self.errores)}")
        
        if self.errores:
            print(f"\n🔍 DETALLE DE ERRORES:")
            for error in self.errores:
                print(f"   - Fila {error.get('fila', 'N/A')}: {error['error']}")
        
        return len(self.exitosos), len(self.errores)

def main():
    """Función principal del script"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Importar equipos desde archivo Excel')
    parser.add_argument('archivo', help='Ruta al archivo Excel')
    parser.add_argument('--test', action='store_true', 
                       help='Modo de prueba (no guarda cambios)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.archivo):
        print(f"❌ Error: El archivo {args.archivo} no existe")
        return 1
    
    try:
        # Crear importador
        importador = ImportadorExcel(args.archivo)
        
        # Validar archivo
        if not importador.validar_archivo():
            return 1
        
        # Limpiar datos
        if not importador.limpiar_datos():
            return 1
        
        print(f"\n📋 Vista previa de datos:")
        print(importador.df.head().to_string())
        
        if args.test:
            print(f"\n🧪 MODO DE PRUEBA - No se guardarán cambios")
            return 0
        
        # Confirmar importación
        respuesta = input(f"\n¿Desea proceder con la importación de {len(importador.df)} equipos? (s/N): ")
        if respuesta.lower() != 's':
            print("Importación cancelada por el usuario")
            return 0
        
        # Importar datos
        exitosos, errores = importador.importar_datos()
        
        if errores > 0:
            print(f"\n⚠️  Se completó con {errores} errores")
            return 1 if errores > exitosos else 0
        else:
            print(f"\n🎉 Importación completada exitosamente!")
            return 0
    
    except Exception as e:
        print(f"❌ Error fatal: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
