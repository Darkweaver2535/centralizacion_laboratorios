#!/usr/bin/env python
"""
Script para verificar la distribución de equipos e insumos por sección
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from insumos.models import Insumo

def verificar_distribucion():
    print('\n=== EQUIPOS ===')
    equipos_total = Equipo.objects.count()
    equipos_academico = Equipo.objects.filter(seccion='academico').count()
    equipos_investigacion = Equipo.objects.filter(seccion='investigacion').count()
    equipos_produccion = Equipo.objects.filter(seccion='produccion').count()
    
    print(f'Total: {equipos_total}')
    print(f'Académico: {equipos_academico}')
    print(f'Investigación: {equipos_investigacion}')
    print(f'Producción: {equipos_produccion}')
    
    # Mostrar algunos IDs de equipos de investigación
    if equipos_investigacion > 0:
        print(f'\nPrimeros 5 equipos de investigación:')
        for equipo in Equipo.objects.filter(seccion='investigacion')[:5]:
            print(f'  - ID {equipo.id}: {equipo.equipo_existente}')
    
    print('\n=== INSUMOS ===')
    insumos_total = Insumo.objects.count()
    insumos_academico = Insumo.objects.filter(seccion='academico').count()
    insumos_investigacion = Insumo.objects.filter(seccion='investigacion').count()
    insumos_produccion = Insumo.objects.filter(seccion='produccion').count()
    
    print(f'Total: {insumos_total}')
    print(f'Académico: {insumos_academico}')
    print(f'Investigación: {insumos_investigacion}')
    print(f'Producción: {insumos_produccion}')
    
    # Mostrar algunos IDs de insumos de investigación
    if insumos_investigacion > 0:
        print(f'\nPrimeros 5 insumos de investigación:')
        for insumo in Insumo.objects.filter(seccion='investigacion')[:5]:
            print(f'  - ID {insumo.id}: {insumo.nombre_elemento}')

if __name__ == '__main__':
    verificar_distribucion()
