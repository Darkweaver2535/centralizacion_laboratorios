#!/usr/bin/env python
"""
Script para actualizar las unidades académicas y carreras con los datos oficiales de EMI
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera
from django.db import transaction

def actualizar_unidades_oficiales():
    """Actualiza las unidades académicas con las abreviaturas oficiales"""
    
    # Mapeo de unidades antiguas a nuevas
    mapeo_unidades = {
        'UASC': 'UASC',  # Se mantiene igual
        'UARIBE': 'UCRB',  # Riberalta cambia a UCRB
        'UATROP': 'UATP',  # Trópico cambia a UATP
        'UACBBA': 'UACB',  # Cochabamba cambia a UACB
    }
    
    print("🔄 Iniciando actualización de unidades académicas...")
    
    with transaction.atomic():
        # Actualizar unidades existentes
        for unidad_antigua, unidad_nueva in mapeo_unidades.items():
            try:
                unidad = UnidadAcademica.objects.get(nombre=unidad_antigua)
                if unidad_antigua != unidad_nueva:
                    print(f"  ✅ Actualizando {unidad_antigua} → {unidad_nueva}")
                    unidad.nombre = unidad_nueva
                    unidad.save()
                else:
                    print(f"  ℹ️  {unidad_antigua} se mantiene igual")
            except UnidadAcademica.DoesNotExist:
                print(f"  ⚠️  Unidad {unidad_antigua} no encontrada")
        
        # Crear UALP si no existe
        if not UnidadAcademica.objects.filter(nombre='UALP').exists():
            UnidadAcademica.objects.create(
                nombre='UALP',
                descripcion='Unidad Académica La Paz'
            )
            print("  ✅ Creada nueva unidad: UALP")
    
    print("✅ Actualización de unidades académicas completada\n")

def mostrar_unidades_actuales():
    """Muestra las unidades académicas actuales"""
    print("📋 Unidades Académicas Oficiales:")
    unidades = UnidadAcademica.objects.all().order_by('nombre')
    for unidad in unidades:
        print(f"  • {unidad.nombre}: {unidad.get_nombre_display()}")
    print()

def mostrar_carreras_disponibles():
    """Muestra las carreras oficiales disponibles"""
    print("📋 Carreras Oficiales Disponibles (19):")
    carreras_oficiales = [
        'Ingeniería Civil',
        'Ingeniería Comercial', 
        'Ingeniería Industrial',
        'Ingeniería Mecánica',
        'Ingeniería Mecatrónica',
        'Ingeniería Petrolera',
        'Ingeniería Química',
        'Ingeniería de Sistemas',
        'Técnico Superior en Electrónica',
        'Técnico Superior en Mecánica Industrial',
        'Técnico Superior en Construcciones Civiles',
        'Técnico Superior en Electromecánica',
        'Técnico Superior en Química Industrial',
        'Técnico Superior en Sistemas',
        'Técnico Superior en Topografía',
        'Licenciatura en Biotecnología',
        'Medicina',
        'Enfermería',
        'Derecho'
    ]
    
    for i, carrera in enumerate(carreras_oficiales, 1):
        print(f"  {i:2d}. {carrera}")
    print()

if __name__ == "__main__":
    print("🏛️  ACTUALIZACIÓN DE DATOS OFICIALES EMI")
    print("=" * 50)
    
    # Mostrar estado actual
    print("📊 Estado actual:")
    print(f"   Unidades académicas: {UnidadAcademica.objects.count()}")
    print(f"   Carreras registradas: {Carrera.objects.count()}")
    print()
    
    # Actualizar unidades
    actualizar_unidades_oficiales()
    
    # Mostrar resultados
    mostrar_unidades_actuales()
    mostrar_carreras_disponibles()
    
    print("✅ Actualización completada. El sistema ahora usa los datos oficiales de EMI.")
    print("💡 Las 19 carreras oficiales están disponibles en formularios.")
    print("📝 Unidades académicas actualizadas con abreviaturas oficiales.")
