#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== BÚSQUEDA DE ASIGNATURAS ===")

# Buscar todas las asignaturas que contengan "FISICA"
asignaturas_fisica = Asignatura.objects.filter(nombre__icontains='FISICA')
print(f"Asignaturas con 'FISICA': {asignaturas_fisica.count()}")

for asig in asignaturas_fisica:
    print(f"  ID: {asig.id} - {asig.get_nombre_display()}")

print("\n=== ASIGNATURAS CON CONTENIDOS ANALÍTICOS ===")

# Buscar asignaturas que tengan contenidos analíticos con recursos
asignaturas_con_recursos = Asignatura.objects.filter(
    unidades_didacticas__contenidoanalitico__materialesherramientasequipos__isnull=False
).distinct()

print(f"Asignaturas con recursos: {asignaturas_con_recursos.count()}")

for asig in asignaturas_con_recursos[:10]:  # Mostrar solo las primeras 10
    contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig)
    recursos_total = sum(
        MaterialesHerramientasEquipos.objects.filter(contenido_analitico=c).count() 
        for c in contenidos
    )
    print(f"  ID: {asig.id} - {asig.get_nombre_display()} ({recursos_total} recursos)")

print("\n=== FIN BÚSQUEDA ===")