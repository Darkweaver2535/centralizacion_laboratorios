"""
Script para probar las vistas AJAX directamente
"""

import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from insumos.models import Insumo
from core.models import UnidadAcademica

print("=== VERIFICACIÓN DE DATOS PARA AJAX ===")
print(f"Fecha: {datetime.now()}")

# Verificar unidades académicas
print("\n--- Unidades Académicas ---")
for unidad in UnidadAcademica.objects.all():
    print(f"ID: {unidad.id}, Nombre: {unidad.nombre}")

# Verificar equipos por unidad
print("\n--- Equipos por Unidad ---")
for unidad in UnidadAcademica.objects.all():
    count = Equipo.objects.filter(unidad_academica=unidad).count()
    print(f"Unidad {unidad.nombre}: {count} equipos")
    if count > 0:
        primer_equipo = Equipo.objects.filter(unidad_academica=unidad).first()
        print(f"  Ejemplo: {primer_equipo.equipo_existente}")

# Verificar insumos por unidad y categoría
print("\n--- Insumos por Unidad y Categoría ---")
for unidad in UnidadAcademica.objects.all():
    materiales = Insumo.objects.filter(unidad_academica=unidad, categoria='materiales').count()
    herramientas = Insumo.objects.filter(unidad_academica=unidad, categoria='herramientas').count()
    reactivos = Insumo.objects.filter(unidad_academica=unidad, categoria='reactivos').count()
    
    print(f"Unidad {unidad.nombre}:")
    print(f"  - Materiales: {materiales}")
    print(f"  - Herramientas: {herramientas}")
    print(f"  - Reactivos: {reactivos}")
    
    if materiales > 0:
        ejemplo = Insumo.objects.filter(unidad_academica=unidad, categoria='materiales').first()
        print(f"  Ejemplo material: {ejemplo.nombre_elemento}")

print("\n=== VERIFICACIÓN COMPLETADA ===")