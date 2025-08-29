#!/usr/bin/env python3
"""
Verificar unidades académicas en filtros
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica
from equipos.models import Equipo

def verificar_unidades_filtros():
    """Verificar que los filtros muestren solo unidades con equipos"""
    
    print("🏫 VERIFICACIÓN DE UNIDADES ACADÉMICAS EN FILTROS")
    print("=" * 50)
    
    print(f"📋 TODAS LAS UNIDADES EN BD:")
    todas_unidades = UnidadAcademica.objects.all()
    for ua in todas_unidades:
        equipos_count = Equipo.objects.filter(unidad_academica=ua).count()
        print(f"   {ua.nombre}: {equipos_count} equipos")
    
    print(f"\n🔍 UNIDADES QUE APARECERÁN EN FILTROS:")
    unidades_con_equipos = UnidadAcademica.objects.filter(
        id__in=Equipo.objects.values_list('unidad_academica_id', flat=True).distinct()
    )
    
    for ua in unidades_con_equipos:
        equipos_count = Equipo.objects.filter(unidad_academica=ua).count()
        print(f"   ✅ {ua.nombre}: {equipos_count:,} equipos")
        if ua.descripcion:
            print(f"      📝 {ua.descripcion}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total unidades en BD: {todas_unidades.count()}")
    print(f"   Unidades en filtros: {unidades_con_equipos.count()}")
    print(f"   Unidades sin equipos: {todas_unidades.count() - unidades_con_equipos.count()}")
    
    # Verificar corrección UCRB → UARB
    print(f"\n✅ VERIFICACIÓN CORRECCIÓN UCRB → UARB:")
    try:
        ucrb = UnidadAcademica.objects.get(nombre='UCRB')
        print(f"   ❌ Todavía existe UCRB: {ucrb.nombre}")
    except UnidadAcademica.DoesNotExist:
        print(f"   ✅ UCRB eliminado correctamente")
    
    try:
        uarb = UnidadAcademica.objects.get(nombre='UARB')
        equipos_count = Equipo.objects.filter(unidad_academica=uarb).count()
        print(f"   ✅ UARB existe: {equipos_count} equipos")
    except UnidadAcademica.DoesNotExist:
        print(f"   ❌ UARB no encontrado")
    
    print(f"\n🚀 Los filtros ahora mostrarán solo unidades con equipos")

if __name__ == "__main__":
    verificar_unidades_filtros()
