#!/usr/bin/env python
"""
Script para distribuir insumos entre las tres secciones:
- 100 insumos a Investigación
- 50 insumos a Producción
- El resto permanece en Académico
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from insumos.models import Insumo

def mover_insumos():
    # Contar insumos actuales
    total = Insumo.objects.count()
    academico = Insumo.objects.filter(seccion='academico').count()
    investigacion = Insumo.objects.filter(seccion='investigacion').count()
    produccion = Insumo.objects.filter(seccion='produccion').count()
    
    print(f'\n=== ESTADO ACTUAL ===')
    print(f'Total insumos: {total}')
    print(f'Académico: {academico}')
    print(f'Investigación: {investigacion}')
    print(f'Producción: {produccion}')
    
    # Obtener insumos académicos para mover
    insumos_academicos = Insumo.objects.filter(seccion='academico')
    
    if insumos_academicos.count() < 150:
        print(f'\n⚠️  No hay suficientes insumos académicos ({insumos_academicos.count()}) para mover 150 (100+50)')
        print(f'Se moverán todos los disponibles...')
    
    # Mover 100 a investigación - obtener IDs primero
    ids_a_investigacion = list(insumos_academicos.values_list('id', flat=True)[:100])
    count_investigacion = Insumo.objects.filter(id__in=ids_a_investigacion).update(seccion='investigacion')
    print(f'\n✓ Movidos {count_investigacion} insumos a Investigación')
    
    # Actualizar queryset después del primer update
    insumos_academicos = Insumo.objects.filter(seccion='academico')
    
    # Mover 50 a producción - obtener IDs primero
    ids_a_produccion = list(insumos_academicos.values_list('id', flat=True)[:50])
    count_produccion = Insumo.objects.filter(id__in=ids_a_produccion).update(seccion='produccion')
    print(f'✓ Movidos {count_produccion} insumos a Producción')
    
    # Contar insumos finales
    academico_final = Insumo.objects.filter(seccion='academico').count()
    investigacion_final = Insumo.objects.filter(seccion='investigacion').count()
    produccion_final = Insumo.objects.filter(seccion='produccion').count()
    
    print(f'\n=== ESTADO FINAL ===')
    print(f'Total insumos: {total}')
    print(f'Académico: {academico_final}')
    print(f'Investigación: {investigacion_final}')
    print(f'Producción: {produccion_final}')

if __name__ == '__main__':
    mover_insumos()
