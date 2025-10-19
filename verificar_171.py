#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== VERIFICAR ASIGNATURA 171 ===")

try:
    asignatura = Asignatura.objects.get(id=171)
    print(f"Asignatura ID 171: {asignatura.get_nombre_display()}")
    
    contenidos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    )
    print(f"Contenidos analíticos: {contenidos.count()}")
    
    for i, contenido in enumerate(contenidos[:3]):  # Solo primeros 3
        print(f"\n--- Contenido {i+1}: {contenido.nombre} ---")
        
        recursos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido)
        procedimientos = Procedimientos.objects.filter(contenido_analitico=contenido)
        bibliografia = Bibliografia.objects.filter(contenido_analitico=contenido)
        
        print(f"  Recursos: {recursos.count()}")
        for r in recursos:
            print(f"    - {r.tipo_elemento}: {r.nombre}")
            
        print(f"  Procedimientos: {procedimientos.count()}")
        for p in procedimientos:
            print(f"    - Paso {p.numero_paso}: {p.titulo_paso}")
            
        print(f"  Bibliografía: {bibliografia.count()}")
        for b in bibliografia:
            print(f"    - {b.titulo}")
            
except Exception as e:
    print(f"Error: {e}")

print("\n=== FIN VERIFICACIÓN ===")