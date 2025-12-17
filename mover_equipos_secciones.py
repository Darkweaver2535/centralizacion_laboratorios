#!/usr/bin/env python
"""
Script para distribuir equipos entre las tres secciones:
- 200 equipos a Investigación
- 100 equipos a Producción
- El resto permanece en Académico
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo

def mover_equipos():
    # Contar equipos actuales
    total = Equipo.objects.count()
    academico = Equipo.objects.filter(seccion='academico').count()
    investigacion = Equipo.objects.filter(seccion='investigacion').count()
    produccion = Equipo.objects.filter(seccion='produccion').count()
    
    print(f'\n=== ESTADO ACTUAL ===')
    print(f'Total equipos: {total}')
    print(f'Académico: {academico}')
    print(f'Investigación: {investigacion}')
    print(f'Producción: {produccion}')
    
    # Obtener equipos académicos para mover
    equipos_academicos = Equipo.objects.filter(seccion='academico')
    
    if equipos_academicos.count() < 300:
        print(f'\n⚠️  No hay suficientes equipos académicos ({equipos_academicos.count()}) para mover 300 (200+100)')
        print(f'Se moverán todos los disponibles...')
    
    # Mover 200 a investigación - obtener IDs primero
    ids_a_investigacion = list(equipos_academicos.values_list('id', flat=True)[:200])
    count_investigacion = Equipo.objects.filter(id__in=ids_a_investigacion).update(seccion='investigacion')
    print(f'\n✓ Movidos {count_investigacion} equipos a Investigación')
    
    # Actualizar queryset después del primer update
    equipos_academicos = Equipo.objects.filter(seccion='academico')
    
    # Mover 100 a producción - obtener IDs primero
    ids_a_produccion = list(equipos_academicos.values_list('id', flat=True)[:100])
    count_produccion = Equipo.objects.filter(id__in=ids_a_produccion).update(seccion='produccion')
    print(f'✓ Movidos {count_produccion} equipos a Producción')
    
    # Contar equipos finales
    academico_final = Equipo.objects.filter(seccion='academico').count()
    investigacion_final = Equipo.objects.filter(seccion='investigacion').count()
    produccion_final = Equipo.objects.filter(seccion='produccion').count()
    
    print(f'\n=== ESTADO FINAL ===')
    print(f'Total equipos: {total}')
    print(f'Académico: {academico_final}')
    print(f'Investigación: {investigacion_final}')
    print(f'Producción: {produccion_final}')

if __name__ == '__main__':
    mover_equipos()
