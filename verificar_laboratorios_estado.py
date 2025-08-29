#!/usr/bin/env python3
"""
Script para verificar el estado actual de laboratorios y equipos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Laboratorio
from equipos.models import Equipo
from django.db.models import Count

def verificar_laboratorios():
    """Verificar el estado actual de laboratorios y equipos"""
    
    print("🔬 VERIFICACIÓN DE LABORATORIOS Y EQUIPOS")
    print("=" * 45)
    
    # Laboratorios disponibles
    laboratorios = Laboratorio.objects.all().order_by('nombre')
    print(f"📋 LABORATORIOS DISPONIBLES ({laboratorios.count()}):")
    for i, lab in enumerate(laboratorios, 1):
        print(f"  {i:2d}. {lab.get_nombre_display()}")
    
    # Estadísticas de equipos por laboratorio
    print(f"\n⚙️ EQUIPOS POR LABORATORIO:")
    equipos_por_lab = Equipo.objects.values('laboratorio__nombre').annotate(
        total=Count('id')
    ).order_by('-total')
    
    total_equipos = Equipo.objects.count()
    print(f"   Total de equipos: {total_equipos}")
    
    for item in equipos_por_lab:
        lab_nombre = item['laboratorio__nombre']
        if lab_nombre:
            try:
                lab = Laboratorio.objects.get(nombre=lab_nombre)
                lab_display = lab.get_nombre_display()
            except Laboratorio.DoesNotExist:
                lab_display = lab_nombre
            total = item['total']
            porcentaje = (total / total_equipos * 100) if total_equipos > 0 else 0
            print(f"   📍 {lab_display}: {total} equipos ({porcentaje:.1f}%)")
        else:
            total = item['total']
            porcentaje = (total / total_equipos * 100) if total_equipos > 0 else 0
            print(f"   ❓ Sin laboratorio: {total} equipos ({porcentaje:.1f}%)")
    
    # Verificar laboratorios del Excel
    print(f"\n⭐ LABORATORIOS PRINCIPALES DEL EXCEL:")
    labs_excel = [
        'LAB_TRATAMIENTO_AGUAS',
        'LAB_ASFALTOS', 
        'LAB_HORMIGONES',
        'LAB_RESISTENCIA_MATERIALES',
        'LAB_LACTEOS'
    ]
    
    for lab_code in labs_excel:
        try:
            lab = Laboratorio.objects.get(nombre=lab_code)
            equipos_count = Equipo.objects.filter(laboratorio=lab).count()
            print(f"   ✅ {lab.get_nombre_display()}: {equipos_count} equipos")
        except Laboratorio.DoesNotExist:
            print(f"   ❌ {lab_code}: No encontrado")
    
    # Responsables únicos
    print(f"\n👤 RESPONSABLES ÚNICOS:")
    responsables = Equipo.objects.exclude(
        responsable_excel__isnull=True
    ).exclude(
        responsable_excel=''
    ).values_list('responsable_excel', flat=True).distinct().order_by('responsable_excel')
    
    print(f"   Total responsables: {responsables.count()}")
    for i, responsable in enumerate(responsables, 1):
        equipos_count = Equipo.objects.filter(responsable_excel=responsable).count()
        print(f"   {i:2d}. {responsable} ({equipos_count} equipos)")

if __name__ == "__main__":
    verificar_laboratorios()
