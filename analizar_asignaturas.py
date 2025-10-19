#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== ESTADO ACTUAL DE ASIGNATURAS ===")

asignaturas_principales = [
    ("FISICA I", 168),
    ("QUIMICA GENERAL", 169), 
    ("FISICA II", 170),
    ("FISICOQUIMICA", 171)
]

print("Asignaturas esperadas:")
for nombre, id_esperado in asignaturas_principales:
    try:
        asig = Asignatura.objects.get(id=id_esperado)
        contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
        recursos = MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico__unidad_didactica__asignatura=asig
        ).count()
        print(f"  ID {id_esperado}: {asig.get_nombre_display()} - {contenidos} contenidos, {recursos} recursos")
    except Asignatura.DoesNotExist:
        print(f"  ID {id_esperado}: {nombre} - NO EXISTE")

print("\nAsignaturas problemáticas con nombres numéricos:")
asignaturas_numericas = Asignatura.objects.filter(nombre__regex=r'^\d+$').order_by('id')

for asig in asignaturas_numericas:
    contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
    recursos = MaterialesHerramientasEquipos.objects.filter(
        contenido_analitico__unidad_didactica__asignatura=asig
    ).count()
    print(f"  ID {asig.id}: '{asig.nombre}' - {contenidos} contenidos, {recursos} recursos")

print(f"\n=== VERIFICACIÓN DE 'PRUEBA LABUBU' ===")
titulos_labubu = Titulo.objects.filter(texto__icontains='LABUBU')
for titulo in titulos_labubu:
    contenido = titulo.contenido_analitico
    asig = contenido.unidad_didactica.asignatura
    print(f"PRUEBA LABUBU está en:")
    print(f"  - Asignatura ID {asig.id}: '{asig.nombre}'")
    print(f"  - Contenido ID {contenido.id}: '{contenido.nombre}'")
    print(f"  - Unidad didáctica: '{contenido.unidad_didactica.nombre}'")

print("\n=== SOLUCIÓN PROPUESTA ===")
print("Opción 1: Mover datos de asignaturas numéricas a las reales")
print("Opción 2: Corregir el formulario para que use las asignaturas correctas")
print("Opción 3: Limpiar y reorganizar todo")

print("\n=== FIN ANÁLISIS ===")