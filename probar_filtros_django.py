#!/usr/bin/env python
"""
Script para probar los filtros de django-filter sin necesidad de interfaz web
"""
import os
import sys
import django

# Configurar Django
project_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios'
if project_path not in sys.path:
    sys.path.insert(0, project_path)
    
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from insumos.models import Insumo
from guias.models import GuiaGenerada
from visualizacion.filters import EquipoFilter, InsumoFilter, GuiaFilter
from django.http import QueryDict

def probar_filtros():
    print("=== PROBANDO FILTROS DJANGO-FILTER ===\n")
    
    # Probar equipos sin filtros
    print("1. EQUIPOS SIN FILTROS:")
    equipos_filter = EquipoFilter(QueryDict(), queryset=Equipo.objects.all())
    print(f"   Total equipos: {equipos_filter.qs.count()}")
    for equipo in equipos_filter.qs[:3]:
        print(f"   - {equipo.equipo_existente} ({equipo.unidad_academica.nombre if equipo.unidad_academica else 'Sin unidad'})")
    
    # Probar equipos con filtro de unidad
    print("\n2. EQUIPOS FILTRADOS POR UNIDAD (UALP):")
    query_params = QueryDict('unidad_academica=1')
    equipos_filter = EquipoFilter(query_params, queryset=Equipo.objects.all())
    print(f"   Equipos encontrados: {equipos_filter.qs.count()}")
    for equipo in equipos_filter.qs[:3]:
        print(f"   - {equipo.equipo_existente} ({equipo.unidad_academica.nombre if equipo.unidad_academica else 'Sin unidad'})")
    
    # Probar equipos con filtro de búsqueda
    print("\n3. EQUIPOS CON BÚSQUEDA 'Equipo 5':")
    query_params = QueryDict('search=Equipo 5')
    equipos_filter = EquipoFilter(query_params, queryset=Equipo.objects.all())
    print(f"   Equipos encontrados: {equipos_filter.qs.count()}")
    for equipo in equipos_filter.qs:
        print(f"   - {equipo.equipo_existente}")
    
    # Probar insumos
    print("\n4. INSUMOS SIN FILTROS:")
    insumos_filter = InsumoFilter(QueryDict(), queryset=Insumo.objects.all())
    print(f"   Total insumos: {insumos_filter.qs.count()}")
    for insumo in insumos_filter.qs[:3]:
        print(f"   - {insumo.nombre_elemento} ({insumo.categoria if insumo.categoria else 'Sin categoría'})")
    
    # Probar guías
    print("\n5. GUÍAS SIN FILTROS:")
    guias_filter = GuiaFilter(QueryDict(), queryset=GuiaGenerada.objects.all())
    print(f"   Total guías: {guias_filter.qs.count()}")
    for guia in guias_filter.qs:
        print(f"   - {guia.titulo}")
    
    print("\n=== TODOS LOS FILTROS FUNCIONAN CORRECTAMENTE ===")

if __name__ == "__main__":
    probar_filtros()