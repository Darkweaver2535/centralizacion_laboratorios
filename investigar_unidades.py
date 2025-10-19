#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== INVESTIGACIÓN DE UNIDADES DIDÁCTICAS ===")

# Verificar unidades didácticas existentes
print("Unidades didácticas en QUÍMICA GENERAL (ID 169):")
unidades_quimica = UnidadDidactica.objects.filter(asignatura_id=169)
for unidad in unidades_quimica:
    contenidos = ContenidoAnalitico.objects.filter(unidad_didactica=unidad).count()
    print(f"  - ID {unidad.id}: '{unidad.nombre}' ({contenidos} contenidos)")

print("\nUnidades didácticas en asignatura problemática (ID 176):")
unidades_problema = UnidadDidactica.objects.filter(asignatura_id=176)
for unidad in unidades_problema:
    contenidos = ContenidoAnalitico.objects.filter(unidad_didactica=unidad).count()
    print(f"  - ID {unidad.id}: '{unidad.nombre}' ({contenidos} contenidos)")
    
print("\nBuscando nombres duplicados:")
nombres_duplicados = []
for unidad_problema in unidades_problema:
    coincidencias = UnidadDidactica.objects.filter(
        asignatura_id=169, 
        nombre=unidad_problema.nombre
    )
    if coincidencias.exists():
        print(f"  ⚠️ Nombre duplicado: '{unidad_problema.nombre}'")
        print(f"     - En problemática (ID 176): Unidad ID {unidad_problema.id}")
        for coincidencia in coincidencias:
            print(f"     - En QUÍMICA (ID 169): Unidad ID {coincidencia.id}")
        nombres_duplicados.append(unidad_problema.nombre)
    else:
        print(f"  ✅ Nombre único: '{unidad_problema.nombre}'")

print(f"\n=== ESTRATEGIA DE MIGRACIÓN ===")
if nombres_duplicados:
    print("Se encontraron nombres duplicados. Usaremos la unidad existente.")
else:
    print("No hay nombres duplicados, se puede crear nueva unidad.")

print("\n=== FIN INVESTIGACIÓN ===")