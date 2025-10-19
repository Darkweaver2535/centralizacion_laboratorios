#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== VERIFICACIÓN DE DATOS ===")

# Buscar asignatura 169 (FISICA II)
try:
    asignatura = Asignatura.objects.get(id=169)
    print(f"Asignatura encontrada: {asignatura.get_nombre_display()}")
    
    # Buscar contenidos analíticos
    contenidos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    )
    print(f"Contenidos analíticos encontrados: {contenidos.count()}")
    
    for contenido in contenidos:
        print(f"\n--- Contenido: {contenido.nombre} ---")
        
        # Verificar materiales/equipos/herramientas
        recursos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido)
        print(f"Recursos: {recursos.count()}")
        for recurso in recursos:
            print(f"  - {recurso.tipo_elemento}: {recurso.nombre}")
            
        # Verificar procedimientos
        procedimientos = Procedimientos.objects.filter(contenido_analitico=contenido)
        print(f"Procedimientos: {procedimientos.count()}")
        for proc in procedimientos:
            print(f"  - Paso {proc.numero_paso}: {proc.titulo_paso}")
            
        # Verificar bibliografía
        bibliografia = Bibliografia.objects.filter(contenido_analitico=contenido)
        print(f"Bibliografía: {bibliografia.count()}")
        for bib in bibliografia:
            print(f"  - {bib.titulo}")
            
except Asignatura.DoesNotExist:
    print("Asignatura 169 no encontrada")

print("\n=== FIN VERIFICACIÓN ===")