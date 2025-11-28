#!/usr/bin/env python
"""
Script para importar equipos de las tres unidades académicas:
- UALP (La Paz)
- UACB (Cochabamba)
- UASC (Santa Cruz)

Los datos vienen de archivos Excel ubicados en:
- pruebas/UALP/TABLA PLANA EQUIPOS-UALP.xlsx
- pruebas/UACB/TABLA PLANA EQUIPOS UACB.xlsx
- pruebas/UASC/TABLA PLANA EQUIPOOS-UASC.xlsx
"""

import os
import sys
import django
import pandas as pd
from decimal import Decimal
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica, Carrera, Asignatura, GuiaLaboratorio, Practica, Laboratorio
from django.contrib.auth import get_user_model

User = get_user_model()

def normalizar_estado(estado_excel):
    """Normaliza el estado del equipo del Excel al modelo"""
    if pd.isna(estado_excel):
        return 'bueno'
    
    estado_str = str(estado_excel).strip().lower()
    
    mapeo_estados = {
        'bueno': 'bueno',
        'regular': 'regular',
        'malo': 'malo',
        'excelente': 'bueno',
        'operativo': 'bueno',
        'inoperativo': 'malo',
        'baja': 'malo',
    }
    
    for key, value in mapeo_estados.items():
        if key in estado_str:
            return value
    
    return 'bueno'

def obtener_o_crear_laboratorio_por_defecto(unidad_academica):
    """Obtiene o crea un laboratorio por defecto para la unidad académica"""
    laboratorio, created = Laboratorio.objects.get_or_create(
        nombre=f'LAB_GENERAL_{unidad_academica.nombre}',
        defaults={
            'descripcion': f'Laboratorio General - {unidad_academica.nombre}',
            'ubicacion': f'Edificio {unidad_academica.nombre}',
            'capacidad': 30,
            'responsable': 'Por asignar'
        }
    )
    if created:
        print(f"  ✅ Laboratorio creado: {laboratorio.nombre}")
    return laboratorio

def obtener_carrera_por_defecto(unidad_academica):
    """Obtiene una carrera por defecto para la unidad académica"""
    # Intentar obtener una carrera de la unidad académica
    carrera = Carrera.objects.filter(unidad_academica=unidad_academica).first()
    
    if not carrera:
        # Si no hay carreras, usar la primera disponible
        carrera = Carrera.objects.first()
    
    return carrera

def obtener_asignatura_por_defecto():
    """Obtiene una asignatura por defecto"""
    return Asignatura.objects.first()

def obtener_guia_por_defecto():
    """Obtiene una guía de laboratorio por defecto"""
    guia = GuiaLaboratorio.objects.first()
    if not guia:
        print("  ⚠️  No hay guías de laboratorio, creando una por defecto...")
        # Necesitamos crear una guía genérica
        from core.models import UnidadTematica
        unidad_tematica = UnidadTematica.objects.first()
        if not unidad_tematica:
            # Crear una unidad temática por defecto
            asignatura = obtener_asignatura_por_defecto()
            unidad_tematica = UnidadTematica.objects.create(
                asignatura=asignatura,
                numero=1,
                nombre="Unidad Temática General",
                descripcion="Unidad temática por defecto"
            )
        guia = GuiaLaboratorio.objects.create(
            unidad_tematica=unidad_tematica,
            numero=1,
            nombre="Guía General",
            descripcion="Guía de laboratorio general"
        )
    return guia

def obtener_practica_por_defecto():
    """Obtiene una práctica por defecto"""
    practica = Practica.objects.first()
    if not practica:
        print("  ⚠️  No hay prácticas, creando una por defecto...")
        guia = obtener_guia_por_defecto()
        practica = Practica.objects.create(
            guia_laboratorio=guia,
            numero=1,
            nombre="Práctica General",
            descripcion="Práctica de laboratorio general"
        )
    return practica

def importar_archivo(ruta_archivo, codigo_unidad):
    """
    Importa equipos desde un archivo Excel a la unidad académica especificada
    
    Args:
        ruta_archivo: Ruta al archivo Excel
        codigo_unidad: Código de la unidad académica (UALP, UACB, UASC)
    """
    print(f"\n{'='*70}")
    print(f"📂 Importando equipos desde: {ruta_archivo}")
    print(f"🏛️  Unidad Académica: {codigo_unidad}")
    print(f"{'='*70}")
    
    # Verificar que el archivo existe
    if not os.path.exists(ruta_archivo):
        print(f"❌ ERROR: El archivo no existe: {ruta_archivo}")
        return
    
    # Obtener la unidad académica
    try:
        unidad_academica = UnidadAcademica.objects.get(nombre=codigo_unidad)
        print(f"✅ Unidad académica encontrada: {unidad_academica.nombre}")
    except UnidadAcademica.DoesNotExist:
        print(f"❌ ERROR: Unidad académica '{codigo_unidad}' no existe en la base de datos")
        return
    
    # Leer el archivo Excel
    try:
        df = pd.read_excel(ruta_archivo)
        print(f"📊 Total de filas en el archivo: {len(df)}")
        print(f"📋 Columnas: {list(df.columns)}")
    except Exception as e:
        print(f"❌ ERROR al leer el archivo Excel: {e}")
        return
    
    # Obtener el usuario administrador
    usuario = User.objects.filter(is_superuser=True).first()
    if not usuario:
        print("❌ ERROR: No hay usuarios administradores en el sistema")
        return
    
    # Obtener datos por defecto
    print("\n🔧 Preparando datos por defecto...")
    laboratorio_default = obtener_o_crear_laboratorio_por_defecto(unidad_academica)
    carrera_default = obtener_carrera_por_defecto(unidad_academica)
    asignatura_default = obtener_asignatura_por_defecto()
    guia_default = obtener_guia_por_defecto()
    practica_default = obtener_practica_por_defecto()
    
    if not all([carrera_default, asignatura_default, guia_default, practica_default]):
        print("❌ ERROR: No se pudieron obtener los datos por defecto necesarios")
        return
    
    print(f"  ✓ Laboratorio: {laboratorio_default.nombre}")
    print(f"  ✓ Carrera: {carrera_default.nombre}")
    print(f"  ✓ Asignatura: {asignatura_default.nombre}")
    print(f"  ✓ Guía: {guia_default.nombre}")
    print(f"  ✓ Práctica: {practica_default.nombre}")
    
    # Normalizar nombres de columnas (eliminar saltos de línea y espacios extras)
    df.columns = [str(col).replace('\n', ' ').strip() for col in df.columns]
    
    # Importar equipos
    print(f"\n⚙️  Importando equipos...")
    equipos_creados = 0
    equipos_saltados = 0
    errores = 0
    
    for index, row in df.iterrows():
        try:
            # Extraer datos del Excel
            descripcion = str(row.get('DESCRIPCION DEL ACTIVO', '')).strip() if pd.notna(row.get('DESCRIPCION DEL ACTIVO')) else ''
            
            # Saltar filas vacías
            if not descripcion or descripcion == '' or descripcion == 'nan':
                equipos_saltados += 1
                continue
            
            # Datos del equipo
            codigo = str(row.get('CODIGO', '')).strip() if pd.notna(row.get('CODIGO')) else ''
            estado_excel = row.get('ESTADO', 'Regular')
            estado = normalizar_estado(estado_excel)
            
            # Datos del responsable
            responsable = str(row.get('RESPONSABLE', '')).strip() if pd.notna(row.get('RESPONSABLE')) else ''
            ci = str(row.get('C.I.', '')).strip() if pd.notna(row.get('C.I.')) else ''
            cargo = str(row.get('CARGO', '')).strip() if pd.notna(row.get('CARGO')) else ''
            oficina = str(row.get('OFICINA', '')).strip() if pd.notna(row.get('OFICINA')) else ''
            
            # Crear el equipo
            equipo = Equipo.objects.create(
                # Campos obligatorios con valores por defecto
                unidad_academica=unidad_academica,
                carrera=carrera_default,
                semestre=1,
                asignatura=asignatura_default,
                carga_horaria_semanal=4,
                carga_horaria_semestral=64,
                guia_laboratorio=guia_default,
                practica=practica_default,
                
                # Datos del equipo desde el Excel
                equipo_existente=descripcion[:200],  # Limitar a 200 caracteres
                marca='',  # No viene en el Excel
                modelo='',  # No viene en el Excel
                estado=estado,
                numero_unidades=1,
                es_activo_fijo=True if codigo else False,
                
                # Ubicación
                laboratorio=laboratorio_default,
                seccion_area=oficina[:100] if oficina else '',
                identificador_aula='',
                
                # Equipos requeridos
                equipo_requerido='',
                numero_equipos_requeridos=0,
                
                # Datos adicionales del Excel
                usuario_creador=usuario,
                responsable_excel=responsable[:200] if responsable else '',
                ci_responsable=ci[:20] if ci else '',
                cargo_responsable=cargo[:200] if cargo else '',
                oficina=oficina[:200] if oficina else '',
                codigo_excel=codigo[:50] if codigo else '',
            )
            
            equipos_creados += 1
            
            # Mostrar progreso cada 100 equipos
            if equipos_creados % 100 == 0:
                print(f"  ⏳ Procesados: {equipos_creados} equipos...")
        
        except Exception as e:
            errores += 1
            if errores <= 5:  # Mostrar solo los primeros 5 errores
                print(f"  ⚠️  Error en fila {index + 1}: {str(e)[:100]}")
    
    # Resumen
    print(f"\n{'='*70}")
    print(f"✅ IMPORTACIÓN COMPLETADA - {codigo_unidad}")
    print(f"{'='*70}")
    print(f"  📊 Total de filas procesadas: {len(df)}")
    print(f"  ✅ Equipos creados: {equipos_creados}")
    print(f"  ⏭️  Equipos saltados: {equipos_saltados}")
    print(f"  ❌ Errores: {errores}")
    print(f"{'='*70}\n")

def main():
    """Función principal"""
    print("="*70)
    print("🚀 IMPORTACIÓN DE EQUIPOS DE TRES UNIDADES ACADÉMICAS")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Definir archivos a importar
    archivos = [
        {
            'ruta': 'pruebas/UALP/TABLA PLANA EQUIPOS-UALP.xlsx',
            'unidad': 'UALP'
        },
        {
            'ruta': 'pruebas/UACB/TABLA PLANA EQUIPOS UACB.xlsx',
            'unidad': 'UACB'
        },
        {
            'ruta': 'pruebas/UASC/TABLA PLANA EQUIPOOS-UASC.xlsx',
            'unidad': 'UASC'
        }
    ]
    
    # Importar cada archivo
    total_creados = 0
    for archivo in archivos:
        resultado = importar_archivo(archivo['ruta'], archivo['unidad'])
        
    # Resumen final
    print("\n" + "="*70)
    print("🎉 PROCESO COMPLETADO")
    print("="*70)
    print(f"\n📊 Estadísticas finales:")
    
    for unidad_codigo in ['UALP', 'UACB', 'UASC']:
        try:
            unidad = UnidadAcademica.objects.get(nombre=unidad_codigo)
            total = Equipo.objects.filter(unidad_academica=unidad).count()
            print(f"  • {unidad_codigo}: {total} equipos en total")
        except UnidadAcademica.DoesNotExist:
            print(f"  • {unidad_codigo}: Unidad no encontrada")
    
    print("\n✅ Los equipos están disponibles en: http://127.0.0.1:8000/visualizacion/?categoria=equipos")
    print("="*70)

if __name__ == "__main__":
    main()
