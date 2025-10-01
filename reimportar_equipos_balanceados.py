#!/usr/bin/env python3
"""
Script para re-importar equipos del Excel con distribución correcta de carreras y asignaturas
"""

import os
import django
import pandas as pd
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica, Carrera, Asignatura
from django.contrib.auth import get_user_model

def limpiar_equipos_actuales():
    """Eliminar todos los equipos actuales"""
    print("🧹 LIMPIANDO EQUIPOS ACTUALES...")
    equipos_count = Equipo.objects.count()
    Equipo.objects.all().delete()
    print(f"✅ Eliminados {equipos_count} equipos")

def importar_equipos_balanceados():
    """Importar equipos del Excel con distribución balanceada"""
    
    excel_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/completo.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Error: No se encontró el archivo {excel_path}")
        return
    
    print(f"📄 Leyendo Excel: {excel_path}")
    
    try:
        # Leer el Excel
        df = pd.read_excel(excel_path)
        print(f"✅ Excel leído: {len(df)} filas")
        
        # Obtener datos necesarios
        ualp = UnidadAcademica.objects.filter(nombre='UALP').first()
        if not ualp:
            print("❌ Error: No se encontró UALP")
            return
        
        # Obtener todas las carreras disponibles
        carreras = list(Carrera.objects.all())
        print(f"📚 Carreras disponibles: {len(carreras)}")
        for carrera in carreras:
            print(f"  - {carrera}")
        
        # Obtener todas las asignaturas de laboratorio
        asignaturas_lab = list(Asignatura.objects.filter(
            nombre__in=['fisica_i', 'quimica_general', 'fisica_ii', 'fisicoquimica']
        ))
        print(f"🧪 Asignaturas de laboratorio: {len(asignaturas_lab)}")
        for asignatura in asignaturas_lab:
            print(f"  - {asignatura}")
        
        # Obtener usuario para asignar
        User = get_user_model()
        usuario = User.objects.first()
        if not usuario:
            print("❌ Error: No hay usuarios en el sistema")
            return
        
        equipos_creados = 0
        equipos_error = 0
        
        print(f"\\n🚀 INICIANDO IMPORTACIÓN DE {len(df)} EQUIPOS...")
        
        for index, row in df.iterrows():
            try:
                # Asignar carrera y asignatura de forma balanceada
                carrera = random.choice(carreras)
                
                # Filtrar asignaturas que pertenezcan a la carrera seleccionada
                asignaturas_carrera = [a for a in asignaturas_lab if a.carrera == carrera]
                if not asignaturas_carrera:
                    # Si no hay asignaturas para esta carrera, usar cualquiera de lab
                    asignatura = random.choice(asignaturas_lab)
                else:
                    asignatura = random.choice(asignaturas_carrera)
                
                # Crear el equipo
                equipo = Equipo.objects.create(
                    unidad_academica=ualp,
                    carrera=carrera,
                    semestre=asignatura.semestre,
                    asignatura=asignatura,
                    carga_horaria_semanal=asignatura.carga_horaria_semanal,
                    carga_horaria_semestral=asignatura.carga_horaria_semestral,
                    equipo_existente=str(row.get('EQUIPO EXISTENTE', '')),
                    marca=str(row.get('MARCA', 'Por definir')),
                    modelo=str(row.get('MODELO', 'Por definir')),
                    estado=row.get('ESTADO', 'REGULAR'),
                    numero_unidades=int(row.get('N° DE UNIDADES', 1)),
                    es_activo_fijo=False,
                    laboratorio_id=1 if hasattr(row, 'LABORATORIO') else None,
                    seccion_area=str(row.get('SECCION/AREA', '')),
                    identificador_aula=str(row.get('IDENTIFICADOR/N° DE AULA', '')),
                    equipo_requerido='',
                    numero_equipos_requeridos=0,
                    responsable_excel=str(row.get('RESPONSABLE', 'No especificado')),
                    observaciones=str(row.get('OBSERVACIONES', '')),
                    usuario_creador=usuario
                )
                
                equipos_creados += 1
                
                # Mostrar progreso cada 500 equipos
                if equipos_creados % 500 == 0:
                    print(f"📊 Progreso: {equipos_creados}/{len(df)} equipos")
                
            except Exception as e:
                equipos_error += 1
                print(f"❌ Error en fila {index}: {e}")
                continue
        
        print(f"\\n🎉 IMPORTACIÓN COMPLETADA:")
        print(f"✅ Equipos creados: {equipos_creados}")
        print(f"❌ Errores: {equipos_error}")
        
        # Verificar distribución
        verificar_distribucion()
        
    except Exception as e:
        print(f"❌ Error general: {e}")

def verificar_distribucion():
    """Verificar la distribución de carreras y asignaturas"""
    
    print(f"\\n📊 VERIFICACIÓN DE DISTRIBUCIÓN:")
    print("=" * 50)
    
    from django.db.models import Count
    
    # Distribución por carreras
    print("🎓 DISTRIBUCIÓN POR CARRERAS:")
    carreras_dist = Equipo.objects.values('carrera__nombre').annotate(count=Count('id')).order_by('-count')
    for carrera in carreras_dist:
        print(f"  - {carrera['carrera__nombre']}: {carrera['count']} equipos")
    
    print()
    # Distribución por asignaturas
    print("📚 DISTRIBUCIÓN POR ASIGNATURAS:")
    asignaturas_dist = Equipo.objects.values('asignatura__nombre').annotate(count=Count('id')).order_by('-count')
    for asignatura in asignaturas_dist:
        print(f"  - {asignatura['asignatura__nombre']}: {asignatura['count']} equipos")

if __name__ == "__main__":
    print("🚀 INICIANDO RE-IMPORTACIÓN DE EQUIPOS")
    print("=" * 60)
    
    # Paso 1: Limpiar equipos actuales
    limpiar_equipos_actuales()
    
    print()
    # Paso 2: Importar con distribución balanceada
    importar_equipos_balanceados()
    
    print()
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
