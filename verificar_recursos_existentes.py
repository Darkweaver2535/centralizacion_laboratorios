#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== CONTENIDOS CON RECURSOS ===")

# Buscar todos los recursos y sus contenidos
recursos = MaterialesHerramientasEquipos.objects.all()

for recurso in recursos:
    contenido = recurso.contenido_analitico
    asignatura = contenido.unidad_didactica.asignatura
    print(f"Recurso: {recurso.nombre} ({recurso.tipo_elemento})")
    print(f"  -> Contenido: {contenido.nombre}")
    print(f"  -> Asignatura: {asignatura.get_nombre_display()} (ID: {asignatura.id})")
    print(f"  -> Unidad: {contenido.unidad_didactica.nombre}")
    print("---")

print(f"\nTotal recursos encontrados: {recursos.count()}")

# Verificar también los procedimientos
print("\n=== PROCEDIMIENTOS ===")
procedimientos = Procedimientos.objects.all()

for proc in procedimientos:
    contenido = proc.contenido_analitico
    asignatura = contenido.unidad_didactica.asignatura
    print(f"Procedimiento: {proc.titulo_paso}")
    print(f"  -> Contenido: {contenido.nombre}")
    print(f"  -> Asignatura: {asignatura.get_nombre_display()} (ID: {asignatura.id})")
    print("---")

print("=== FIN VERIFICACIÓN ===")