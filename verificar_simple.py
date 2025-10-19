#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== VERIFICACIÓN SIMPLE ===")

# Verificar FISICA II (ID 170)
try:
    asignatura = Asignatura.objects.get(id=170)
    print(f"Asignatura ID 170: {asignatura.get_nombre_display()}")
    
    contenidos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    )
    print(f"Contenidos analíticos: {contenidos.count()}")
    
    if contenidos.exists():
        primer_contenido = contenidos.first()
        print(f"Primer contenido: {primer_contenido.nombre}")
        
        recursos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=primer_contenido)
        procedimientos = Procedimientos.objects.filter(contenido_analitico=primer_contenido)
        
        print(f"  - Recursos: {recursos.count()}")
        print(f"  - Procedimientos: {procedimientos.count()}")
        
        if recursos.exists():
            for r in recursos[:3]:
                print(f"    > {r.tipo_elemento}: {r.nombre}")
                
except Asignatura.DoesNotExist:
    print("Asignatura 170 no encontrada")

print("\n=== VERIFICAR TODOS LOS RECURSOS ===")

# Contar todos los recursos en la base de datos
total_recursos = MaterialesHerramientasEquipos.objects.all().count()
total_procedimientos = Procedimientos.objects.all().count()

print(f"Total recursos en BD: {total_recursos}")
print(f"Total procedimientos en BD: {total_procedimientos}")

if total_recursos > 0:
    print("\nPrimeros 5 recursos:")
    for r in MaterialesHerramientasEquipos.objects.all()[:5]:
        asig_nombre = r.contenido_analitico.unidad_didactica.asignatura.get_nombre_display()
        print(f"  - {r.tipo_elemento}: {r.nombre} (Asignatura: {asig_nombre})")

print("\n=== FIN VERIFICACIÓN ===")