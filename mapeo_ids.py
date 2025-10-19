#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== MAPEO DE IDs ===")

# Verificar las asignaturas con IDs específicos
ids_a_verificar = [169, 170, 175, 176]

for asig_id in ids_a_verificar:
    try:
        asignatura = Asignatura.objects.get(id=asig_id)
        contenidos_count = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=asignatura
        ).count()
        recursos_count = MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico__unidad_didactica__asignatura=asignatura
        ).count()
        
        print(f"ID {asig_id}: {asignatura.get_nombre_display()}")
        print(f"  - Contenidos: {contenidos_count}")
        print(f"  - Recursos: {recursos_count}")
        print(f"  - Carrera: {asignatura.carrera.get_nombre_display()}")
        print(f"  - Unidad: {asignatura.carrera.unidad_academica.get_nombre_display()}")
        print("---")
        
    except Asignatura.DoesNotExist:
        print(f"ID {asig_id}: NO EXISTE")
        print("---")

print("=== FIN MAPEO ===")