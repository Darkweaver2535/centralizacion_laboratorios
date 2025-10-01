#!/usr/bin/env python
"""
Script mejorado para re-importar equipos con distribución balanceada incluyendo guías y prácticas
"""

import os
import sys
import django
import pandas as pd
import random
import uuid

# Configuración de Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import (
    UnidadAcademica, Carrera, Asignatura, Laboratorio, 
    GuiaLaboratorio, Practica
)
from usuarios.models import Usuario

def limpiar_equipos_actuales():
    """Eliminar todos los equipos existentes"""
    print("🧹 LIMPIANDO EQUIPOS ACTUALES")
    print("=" * 50)
    
    count = Equipo.objects.count()
    print(f"📊 Equipos a eliminar: {count}")
    
    if count > 0:
        Equipo.objects.all().delete()
        print(f"✅ {count} equipos eliminados")
    else:
        print("ℹ️  No hay equipos para eliminar")

def obtener_referencias_necesarias():
    """Obtener todas las referencias necesarias para crear equipos"""
    print("\n🔍 OBTENIENDO REFERENCIAS NECESARIAS")
    print("=" * 50)
    
    # Obtener todas las carreras
    carreras = list(Carrera.objects.all())
    print(f"🎓 Carreras disponibles: {len(carreras)}")
    
    # Obtener asignaturas de laboratorio
    asignaturas_lab = ['fisica_i', 'quimica_general', 'fisica_ii', 'fisicoquimica']
    asignaturas = []
    guias_practicas = {}
    
    for codigo in asignaturas_lab:
        asignatura = Asignatura.objects.filter(nombre=codigo).first()
        if asignatura:
            asignaturas.append(asignatura)
            # Obtener guía y práctica para esta asignatura
            guia = GuiaLaboratorio.objects.filter(
                unidad_tematica__asignatura=asignatura
            ).first()
            practica = Practica.objects.filter(guia_laboratorio=guia).first() if guia else None
            
            if guia and practica:
                guias_practicas[asignatura.nombre] = {
                    'guia': guia,
                    'practica': practica
                }
                print(f"  ✅ {asignatura.get_nombre_display()}: Guía y práctica encontradas")
            else:
                print(f"  ❌ {asignatura.get_nombre_display()}: Faltan guía o práctica")
    
    print(f"📚 Asignaturas de laboratorio: {len(asignaturas)}")
    
    # Obtener laboratorios
    laboratorios = list(Laboratorio.objects.all())
    print(f"🏢 Laboratorios disponibles: {len(laboratorios)}")
    
    # Obtener unidad académica UALP
    ualp = UnidadAcademica.objects.filter(nombre='UALP').first()
    if not ualp:
        print("❌ UALP no encontrada")
        return None, None, None, None, None, None
    
    # Obtener usuario admin para asignar como creador
    admin_user = Usuario.objects.filter(username='admin').first()
    if not admin_user:
        print("❌ Usuario admin no encontrado")
        return None, None, None, None, None, None
        
    return carreras, asignaturas, laboratorios, guias_practicas, ualp, admin_user

def importar_equipos_balanceados():
    """Importar equipos del Excel con distribución balanceada"""
    print("\n📥 IMPORTANDO EQUIPOS CON DISTRIBUCIÓN BALANCEADA")
    print("=" * 60)
    
    # Obtener referencias
    carreras, asignaturas, laboratorios, guias_practicas, ualp, admin_user = obtener_referencias_necesarias()
    
    if not all([carreras, asignaturas, laboratorios, guias_practicas, ualp, admin_user]):
        print("❌ No se pudieron obtener todas las referencias necesarias")
        return False
    
    # Leer el archivo Excel
    excel_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/1 ACTAS UNIDAD DE INVESTIGACION CIENCIA Y TECNOLOGIA OFICINAS.xlsx'
    
    try:
        df = pd.read_excel(excel_path, sheet_name=0)
        print(f"📄 Excel leído correctamente: {len(df)} filas")
    except Exception as e:
        print(f"❌ Error al leer Excel: {e}")
        return False
    
    # Preparar datos para distribución balanceada
    equipos_exitosos = 0
    equipos_fallidos = 0
    
    for index, row in df.iterrows():
        try:
            # Distribuir aleatoriamente
            carrera = random.choice(carreras)
            asignatura = random.choice(asignaturas)
            laboratorio = random.choice(laboratorios)
            
            # Obtener guía y práctica para la asignatura
            if asignatura.nombre in guias_practicas:
                guia_data = guias_practicas[asignatura.nombre]
                guia = guia_data['guia']
                practica = guia_data['practica']
            else:
                print(f"⚠️  Saltando fila {index + 2}: No hay guía/práctica para {asignatura.nombre}")
                equipos_fallidos += 1
                continue
            
            # Crear el equipo con código único temporal
            codigo_temporal = f"TEMP-{uuid.uuid4().hex[:8].upper()}-{index + 1:04d}"
            
            equipo_data = {
                # Campos obligatorios básicos
                'unidad_academica': ualp,
                'carrera': carrera,
                'semestre': random.randint(1, 10),
                'asignatura': asignatura,
                'carga_horaria_semanal': 4,
                'carga_horaria_semestral': 64,
                
                # Referencias obligatorias
                'guia_laboratorio': guia,
                'practica': practica,
                'laboratorio': laboratorio,
                'usuario_creador': admin_user,
                
                # Datos del equipo del Excel
                'equipo_existente': str(row.get('NOMBRE DE EQUIPO EXISTENTE', f'Equipo {index + 1}')),
                'marca': str(row.get('MARCA', '')),
                'modelo': str(row.get('MODELO', '')),
                'estado': random.choice(['bueno', 'regular', 'malo']),
                'numero_unidades': int(row.get('NÚMERO DE UNIDADES DEL EQUIPO', 1)) if pd.notna(row.get('NÚMERO DE UNIDADES DEL EQUIPO')) else 1,
                'es_activo_fijo': random.choice([True, False]),
                'seccion_area': str(row.get('SECCIÓN/ÁREA', '')),
                'identificador_aula': str(row.get('IDENTIFICADOR/Nº DE AULA', '')),
                'equipo_requerido': str(row.get('EQUIPO REQUERIDO', '')),
                'numero_equipos_requeridos': int(row.get('NÚMERO DE EQUIPOS REQUERIDOS', 1)) if pd.notna(row.get('NÚMERO DE EQUIPOS REQUERIDOS')) else 1,
                'codigo_inventario': codigo_temporal,  # Código temporal único
            }
            
            # Crear el equipo
            equipo = Equipo.objects.create(**equipo_data)
            
            equipos_exitosos += 1
            
            if equipos_exitosos % 500 == 0:
                print(f"✅ Procesados {equipos_exitosos} equipos...")
                
        except Exception as e:
            print(f"❌ Error en fila {index + 2}: {str(e)}")
            equipos_fallidos += 1
            continue
    
    print(f"\n🎉 IMPORTACIÓN COMPLETADA:")
    print(f"✅ Equipos creados: {equipos_exitosos}")
    print(f"❌ Errores: {equipos_fallidos}")
    
    return True

def verificar_distribucion():
    """Verificar la distribución final de equipos"""
    print("\n📊 VERIFICACIÓN DE DISTRIBUCIÓN:")
    print("=" * 50)
    
    # Distribución por carreras
    print("🎓 DISTRIBUCIÓN POR CARRERAS:")
    carreras_dist = {}
    for equipo in Equipo.objects.all():
        carrera_nombre = equipo.carrera.get_nombre_display()
        carreras_dist[carrera_nombre] = carreras_dist.get(carrera_nombre, 0) + 1
    
    for carrera, count in sorted(carreras_dist.items()):
        print(f"  - {carrera}: {count} equipos")
    
    # Distribución por asignaturas
    print("\n📚 DISTRIBUCIÓN POR ASIGNATURAS:")
    asignaturas_dist = {}
    for equipo in Equipo.objects.all():
        asig_nombre = equipo.asignatura.get_nombre_display()
        asignaturas_dist[asig_nombre] = asignaturas_dist.get(asig_nombre, 0) + 1
    
    for asignatura, count in sorted(asignaturas_dist.items()):
        print(f"  - {asignatura}: {count} equipos")

def main():
    """Función principal"""
    print("🚀 INICIANDO REIMPORTACIÓN DE EQUIPOS BALANCEADOS")
    print("=" * 60)
    
    # Paso 1: Limpiar equipos actuales
    limpiar_equipos_actuales()
    
    # Paso 2: Importar con distribución balanceada
    if importar_equipos_balanceados():
        # Paso 3: Verificar distribución
        verificar_distribucion()
        
        print("\n✅ PROCESO COMPLETADO")
        print("=" * 60)
    else:
        print("\n❌ PROCESO FALLIDO")
        print("=" * 60)

if __name__ == "__main__":
    main()
