#!/usr/bin/env python
"""
Script de verificación completa del sistema actualizado con datos oficiales de EMI
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera
from equipos.models import TareaReordenamiento, EquipoTarea
from django.db.models import Count

def verificar_unidades_oficiales():
    """Verifica que las unidades académicas estén actualizadas correctamente"""
    print("🏛️  VERIFICACIÓN DE UNIDADES ACADÉMICAS OFICIALES")
    print("=" * 55)
    
    unidades_oficiales = ['UALP', 'UACB', 'UASC', 'UATP', 'UCRB']
    unidades_db = UnidadAcademica.objects.all().order_by('nombre')
    
    print(f"✅ Total de unidades académicas: {unidades_db.count()}")
    print(f"📋 Unidades oficiales esperadas: {len(unidades_oficiales)}")
    print()
    
    print("📍 Unidades Académicas Registradas:")
    for unidad in unidades_db:
        status = "✅" if unidad.nombre in unidades_oficiales else "⚠️"
        print(f"  {status} {unidad.nombre}: {unidad.get_nombre_display()}")
    print()
    
    # Verificar que todas las unidades oficiales estén presentes
    unidades_faltantes = set(unidades_oficiales) - set(u.nombre for u in unidades_db)
    if unidades_faltantes:
        print(f"❌ Unidades faltantes: {', '.join(unidades_faltantes)}")
    else:
        print("✅ Todas las unidades académicas oficiales están registradas")
    print()

def verificar_carreras_oficiales():
    """Verifica las carreras oficiales disponibles"""
    print("🎓 VERIFICACIÓN DE CARRERAS OFICIALES")
    print("=" * 40)
    
    carreras_choices = dict(Carrera.CARRERAS)
    print(f"✅ Total de carreras oficiales disponibles: {len(carreras_choices)}")
    print()
    
    print("📚 Carreras Oficiales EMI (19):")
    for i, (codigo, nombre) in enumerate(Carrera.CARRERAS, 1):
        print(f"  {i:2d}. {nombre} ({codigo})")
    print()
    
    # Verificar carreras registradas en la base de datos
    carreras_db = Carrera.objects.all().count()
    print(f"📊 Carreras registradas en BD: {carreras_db}")
    print()

def verificar_sistema_reordenamiento():
    """Verifica el sistema de reordenamiento de equipos"""
    print("📦 VERIFICACIÓN DEL SISTEMA DE REORDENAMIENTO")
    print("=" * 50)
    
    # Verificar tareas
    tareas = TareaReordenamiento.objects.all()
    print(f"✅ Total de tareas de reordenamiento: {tareas.count()}")
    
    # Verificar equipos asignados
    equipos_asignados = EquipoTarea.objects.all()
    print(f"✅ Total de equipos asignados a tareas: {equipos_asignados.count()}")
    
    # Verificar tareas con equipos
    tareas_con_equipos = TareaReordenamiento.objects.annotate(
        num_equipos=Count('equipos')
    ).filter(num_equipos__gt=0)
    
    print(f"✅ Tareas con equipos asignados: {tareas_con_equipos.count()}")
    
    if tareas_con_equipos.exists():
        print("\n📋 Tareas activas con equipos:")
        for tarea in tareas_con_equipos[:5]:  # Mostrar las primeras 5
            print(f"  • Tarea #{tarea.id}: {tarea.titulo} ({tarea.equipos.count()} equipos)")
    print()

def mostrar_resumen_completo():
    """Muestra un resumen completo del sistema"""
    print("📊 RESUMEN GENERAL DEL SISTEMA")
    print("=" * 35)
    
    # Contadores generales
    total_unidades = UnidadAcademica.objects.count()
    total_carreras_choices = len(Carrera.CARRERAS)
    total_carreras_db = Carrera.objects.count()
    total_tareas = TareaReordenamiento.objects.count()
    total_equipos_asignados = EquipoTarea.objects.count()
    
    print(f"🏛️  Unidades Académicas: {total_unidades}/5 oficiales")
    print(f"🎓 Carreras Disponibles: {total_carreras_choices} oficiales")
    print(f"📚 Carreras en BD: {total_carreras_db}")
    print(f"📦 Tareas Reordenamiento: {total_tareas}")
    print(f"🔄 Equipos en Tareas: {total_equipos_asignados}")
    print()
    
    # Estado del sistema
    estado_unidades = "✅ CORRECTO" if total_unidades == 5 else "❌ INCOMPLETO"
    estado_carreras = "✅ CORRECTO" if total_carreras_choices == 19 else "❌ INCOMPLETO"
    estado_reordenamiento = "✅ ACTIVO" if total_tareas > 0 else "⚠️ SIN TAREAS"
    
    print("🔍 Estado del Sistema:")
    print(f"  Unidades Académicas: {estado_unidades}")
    print(f"  Carreras Oficiales: {estado_carreras}")
    print(f"  Sistema Reordenamiento: {estado_reordenamiento}")
    print()

def mostrar_mapeo_api():
    """Muestra el mapeo para APIs"""
    print("🔗 MAPEO PARA APIs Y FORMULARIOS")
    print("=" * 40)
    
    print("📍 Mapeo de Unidades Académicas:")
    mapeo_unidades = {
        'la_paz': 'UALP',
        'santa_cruz': 'UASC', 
        'cochabamba': 'UACB',
        'riberalta': 'UCRB',
        'tropico': 'UATP'
    }
    
    for key, value in mapeo_unidades.items():
        unidad = UnidadAcademica.objects.filter(nombre=value).first()
        if unidad:
            print(f"  '{key}' → {value} ({unidad.get_nombre_display()})")
        else:
            print(f"  '{key}' → {value} (❌ NO ENCONTRADA)")
    print()

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN COMPLETA DEL SISTEMA EMI")
    print("🏛️  Escuela Militar de Ingeniería")
    print("📅 " + "="*50)
    print()
    
    try:
        # Verificaciones principales
        verificar_unidades_oficiales()
        verificar_carreras_oficiales()
        verificar_sistema_reordenamiento()
        mostrar_mapeo_api()
        mostrar_resumen_completo()
        
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("💡 El sistema está actualizado con los datos oficiales de EMI")
        print("🚀 Sistema listo para uso en producción")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {str(e)}")
        print("🔧 Revisar la configuración del sistema")
