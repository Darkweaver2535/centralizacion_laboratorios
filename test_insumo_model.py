#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from insumos.models import Insumo

# Verificar los campos del modelo Insumo
print("Campos del modelo Insumo:")
for field in Insumo._meta.fields:
    print(f"- {field.name}: {field.__class__.__name__}")

# Verificar si hay insumos en la base de datos
insumos = Insumo.objects.all()
print(f"\nTotal de insumos: {insumos.count()}")

if insumos.exists():
    primer_insumo = insumos.first()
    print(f"\nPrimer insumo:")
    print(f"- ID: {primer_insumo.id}")
    print(f"- Nombre: {primer_insumo.nombre_elemento}")
    print(f"- Descripción: {primer_insumo.descripcion_caracteristicas}")
    
    # Verificar campos relacionados
    print(f"- Unidad académica: {getattr(primer_insumo, 'unidad_academica', 'NO EXISTE')}")
    print(f"- Carrera: {getattr(primer_insumo, 'carrera', 'NO EXISTE')}")
    print(f"- Asignatura: {getattr(primer_insumo, 'asignatura', 'NO EXISTE')}")
    print(f"- Laboratorio: {getattr(primer_insumo, 'laboratorio', 'NO EXISTE')}")