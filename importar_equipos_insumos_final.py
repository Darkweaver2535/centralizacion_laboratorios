#!/usr/bin/env python3
"""
Script corregido para importar equipos e insumos desde archivos Excel
Con campos correctos y creación de dependencias faltantes
"""

import os
import sys
import django
from datetime import datetime
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion_laboratorios.settings')
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
django.setup()

from django.contrib.auth.models import User
from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio, GuiaLaboratorio, Practica
from equipos.models import Equipo
from insumos.models import Insumo

def crear_dependencias_basicas():
    """Crear usuarios, laboratorios y otros datos básicos necesarios"""
    print("Creando dependencias básicas...")
    
    # Crear usuario por defecto
    usuario, created = User.objects.get_or_create(
        username='sistema',
        defaults={
            'email': 'sistema@uagrm.edu.bo',
            'first_name': 'Sistema',
            'last_name': 'Importación',
            'is_staff': True
        }
    )
    if created:
        usuario.set_password('sistema123')
        usuario.save()
    
    # Obtener unidades académicas
    unidades = UnidadAcademica.objects.all()
    
    # Crear laboratorios básicos para cada unidad
    for unidad in unidades:
        laboratorio, created = Laboratorio.objects.get_or_create(
            nombre=f"Laboratorio General {unidad.abreviatura}",
            unidad_academica=unidad,
            defaults={
                'descripcion': f'Laboratorio general de {unidad.nombre}',
                'ubicacion': f'Edificio {unidad.abreviatura}',
                'capacidad': 20,
                'estado': 'activo'
            }
        )
    
    # Crear guía de laboratorio básica
    guia_default, created = GuiaLaboratorio.objects.get_or_create(
        nombre="Guía General",
        defaults={
            'descripcion': 'Guía de laboratorio general importada desde Excel',
            'autor': 'Sistema',
            'version': '1.0'
        }
    )
    
    # Crear práctica básica
    practica_default, created = Practica.objects.get_or_create(
        numero_practica=1,
        nombre="Práctica General",
        guia_laboratorio=guia_default,
        defaults={
            'descripcion': 'Práctica general importada desde Excel',
            'duracion_horas': 2,
            'objetivos': 'Objetivos de práctica general'
        }
    )
    
    return usuario, guia_default, practica_default

def importar_equipos():
    """Importar equipos desde Excel"""
    print("\n=== IMPORTANDO EQUIPOS ===")
    
    archivo_equipos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'
    
    try:
        df = pd.read_excel(archivo_equipos)
        print(f"Archivo leído correctamente. Total filas: {len(df)}")
        
        # Obtener dependencias básicas
        usuario, guia_default, practica_default = crear_dependencias_basicas()
        
        equipos_creados = 0
        errores = 0
        
        for index, fila in df.iterrows():
            try:
                # Obtener unidad académica
                unidad_nombre = str(fila.get('UNIDAD ACADÉMICA', '')).strip()
                if not unidad_nombre or unidad_nombre == 'nan':
                    print(f"Error en fila {index + 1}: Sin unidad académica")
                    errores += 1
                    continue
                
                unidad = UnidadAcademica.objects.filter(
                    nombre__icontains=unidad_nombre
                ).first()
                
                if not unidad:
                    # Buscar por abreviatura común
                    if 'INDUSTRIAL' in unidad_nombre.upper():
                        unidad = UnidadAcademica.objects.filter(abreviatura='ING_INDUSTRIAL').first()
                    elif 'CIVIL' in unidad_nombre.upper():
                        unidad = UnidadAcademica.objects.filter(abreviatura='ING_CIVIL').first()
                    elif 'SISTEMAS' in unidad_nombre.upper():
                        unidad = UnidadAcademica.objects.filter(abreviatura='ING_SISTEMAS').first()
                    
                if not unidad:
                    print(f"Error en fila {index + 1}: Unidad académica no encontrada: {unidad_nombre}")
                    errores += 1
                    continue
                
                # Obtener carrera (usar la primera carrera de la unidad si no se encuentra)
                carrera_nombre = str(fila.get('CARRERA', '')).strip()
                carrera = Carrera.objects.filter(unidad_academica=unidad).first()
                
                if not carrera:
                    print(f"Error en fila {index + 1}: No hay carreras en la unidad {unidad.nombre}")
                    errores += 1
                    continue
                
                # Obtener asignatura (usar la primera asignatura de la carrera)
                asignatura = Asignatura.objects.filter(carrera=carrera).first()
                
                if not asignatura:
                    print(f"Error en fila {index + 1}: No hay asignaturas en la carrera {carrera.nombre}")
                    errores += 1
                    continue
                
                # Obtener laboratorio
                laboratorio = Laboratorio.objects.filter(unidad_academica=unidad).first()
                
                if not laboratorio:
                    print(f"Error en fila {index + 1}: No hay laboratorio para la unidad {unidad.nombre}")
                    errores += 1
                    continue
                
                # Obtener nombre del equipo
                nombre_equipo = str(fila.get('NOMBRE DE EQUIPO EXISTENTE', '')).strip()
                if not nombre_equipo or nombre_equipo == 'nan':
                    nombre_equipo = f"Equipo {index + 1}"
                
                # Crear equipo
                equipo = Equipo.objects.create(
                    unidad_academica=unidad,
                    carrera=carrera,
                    semestre=1,  # Valor por defecto
                    asignatura=asignatura,
                    carga_horaria_semanal=2,  # Valor por defecto
                    carga_horaria_semestral=32,  # Valor por defecto
                    guia_laboratorio=guia_default,
                    practica=practica_default,
                    equipo_existente=nombre_equipo,
                    marca=str(fila.get('MARCA', '')).strip() if pd.notna(fila.get('MARCA')) else '',
                    modelo=str(fila.get('MODELO', '')).strip() if pd.notna(fila.get('MODELO')) else '',
                    estado='bueno',  # Valor por defecto
                    numero_unidades=1,  # Valor por defecto
                    laboratorio=laboratorio,
                    usuario_creador=usuario,
                    responsable_excel=str(fila.get('RESPONSABLE', '')).strip() if pd.notna(fila.get('RESPONSABLE')) else 'Sistema'
                )
                
                equipos_creados += 1
                
                if equipos_creados % 100 == 0:
                    print(f"Equipos procesados: {equipos_creados}")
                
            except Exception as e:
                print(f"Error en fila {index + 1}: {str(e)}")
                errores += 1
                continue
        
        print(f"Equipos importados: {equipos_creados}")
        print(f"Errores: {errores}")
        
    except Exception as e:
        print(f"Error al leer archivo de equipos: {str(e)}")

def importar_insumos():
    """Importar insumos desde Excel"""
    print("\n=== IMPORTANDO INSUMOS ===")
    
    archivo_insumos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm'
    
    try:
        df = pd.read_excel(archivo_insumos)
        print(f"Archivo leído correctamente. Total filas: {len(df)}")
        
        insumos_creados = 0
        errores = 0
        
        for index, fila in df.iterrows():
            try:
                # Obtener unidad académica
                unidad_nombre = str(fila.get('UNIDAD ACADÉMICA', '')).strip()
                if not unidad_nombre or unidad_nombre == 'nan':
                    print(f"Error en fila {index + 1}: Sin unidad académica")
                    errores += 1
                    continue
                
                unidad = UnidadAcademica.objects.filter(
                    nombre__icontains=unidad_nombre
                ).first()
                
                if not unidad:
                    # Buscar por abreviatura común
                    if 'INDUSTRIAL' in unidad_nombre.upper():
                        unidad = UnidadAcademica.objects.filter(abreviatura='ING_INDUSTRIAL').first()
                    elif 'CIVIL' in unidad_nombre.upper():
                        unidad = UnidadAcademica.objects.filter(abreviatura='ING_CIVIL').first()
                    elif 'SISTEMAS' in unidad_nombre.upper():
                        unidad = UnidadAcademica.objects.filter(abreviatura='ING_SISTEMAS').first()
                
                if not unidad:
                    print(f"Error en fila {index + 1}: Unidad académica no encontrada: {unidad_nombre}")
                    errores += 1
                    continue
                
                # Obtener carrera y asignatura
                carrera = Carrera.objects.filter(unidad_academica=unidad).first()
                if not carrera:
                    print(f"Error en fila {index + 1}: No hay carreras en la unidad {unidad.nombre}")
                    errores += 1
                    continue
                
                asignatura = Asignatura.objects.filter(carrera=carrera).first()
                if not asignatura:
                    print(f"Error en fila {index + 1}: No hay asignaturas en la carrera {carrera.nombre}")
                    errores += 1
                    continue
                
                # Obtener laboratorio
                laboratorio = Laboratorio.objects.filter(unidad_academica=unidad).first()
                if not laboratorio:
                    print(f"Error en fila {index + 1}: No hay laboratorio para la unidad {unidad.nombre}")
                    errores += 1
                    continue
                
                # Obtener nombre del insumo
                nombre_insumo = str(fila.get('NOMBRE DEL ELEMENTO', '')).strip()
                if not nombre_insumo or nombre_insumo == 'nan':
                    nombre_insumo = f"Insumo {index + 1}"
                
                # Determinar categoría
                categoria = 'materiales'  # Valor por defecto
                nombre_lower = nombre_insumo.lower()
                if any(palabra in nombre_lower for palabra in ['químico', 'reactivo', 'ácido', 'base']):
                    categoria = 'reactivos'
                elif any(palabra in nombre_lower for palabra in ['herramienta', 'destornillador', 'martillo']):
                    categoria = 'herramientas'
                
                # Crear insumo
                insumo = Insumo.objects.create(
                    unidad_academica=unidad,
                    laboratorio=laboratorio,
                    categoria=categoria,
                    nombre_elemento=nombre_insumo,
                    descripcion_caracteristicas=str(fila.get('DESCRIPCIÓN/CARACTERÍSTICAS', '')).strip() if pd.notna(fila.get('DESCRIPCIÓN/CARACTERÍSTICAS')) else '',
                    marca_modelo=str(fila.get('MARCA / MODELO', '')).strip() if pd.notna(fila.get('MARCA / MODELO')) else '',
                    estado='bueno',  # Valor por defecto
                    cantidad=1,  # Valor por defecto
                    unidad_medida='unidades',
                    carrera=carrera,
                    asignatura=asignatura
                )
                
                insumos_creados += 1
                
                if insumos_creados % 50 == 0:
                    print(f"Insumos procesados: {insumos_creados}")
                
            except Exception as e:
                print(f"Error en fila {index + 1}: {str(e)}")
                errores += 1
                continue
        
        print(f"Insumos importados: {insumos_creados}")
        print(f"Errores: {errores}")
        
    except Exception as e:
        print(f"Error al leer archivo de insumos: {str(e)}")

def verificar_importacion():
    """Verificar los datos importados"""
    print("\n=== VERIFICACIÓN POST-IMPORTACIÓN ===")
    
    total_equipos = Equipo.objects.count()
    total_insumos = Insumo.objects.count()
    
    print(f"Total equipos: {total_equipos}")
    print(f"Total insumos: {total_insumos}")
    
    print("\n=== DISTRIBUCIÓN POR UNIDAD ===")
    for unidad in UnidadAcademica.objects.all():
        equipos_unidad = Equipo.objects.filter(unidad_academica=unidad).count()
        insumos_unidad = Insumo.objects.filter(unidad_academica=unidad).count()
        print(f"{unidad.abreviatura}: {equipos_unidad} equipos, {insumos_unidad} insumos")

def main():
    """Función principal"""
    print("=== IMPORTACIÓN DE DATOS DE EQUIPOS E INSUMOS ===")
    print(f"Fecha: {datetime.now()}")
    
    # Limpiar datos existentes
    print("Limpiando datos existentes...")
    Equipo.objects.all().delete()
    Insumo.objects.all().delete()
    print("Datos limpiados.")
    
    # Importar datos
    importar_equipos()
    importar_insumos()
    
    # Verificar importación
    verificar_importacion()
    
    print("\n=== IMPORTACIÓN COMPLETADA ===")

if __name__ == "__main__":
    main()