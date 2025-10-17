#!/usr/bin/env python3
"""
Script simple para verificar carreras disponibles en UALP
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, UnidadAcademica

print("🔍 Verificando carreras en UALP...")

try:
    ualp = UnidadAcademica.objects.get(nombre='UALP')
    print(f"✅ Unidad académica: {ualp}")
    
    carreras = Carrera.objects.filter(unidad_academica=ualp)
    print(f"\n📋 Carreras disponibles ({carreras.count()}):")
    
    for carrera in carreras:
        print(f"  - Código: {carrera.nombre}")
        print(f"    Nombre: {carrera.get_nombre_display()}")
        print(f"    ID: {carrera.id}")
        print()
        
except UnidadAcademica.DoesNotExist:
    print("❌ UALP no encontrada")

# Buscar específicamente por 'industrial' en cualquier forma
print("\n🔍 Buscando carreras que contengan 'industrial'...")
carreras_industrial = Carrera.objects.filter(nombre__icontains='industrial')
for carrera in carreras_industrial:
    print(f"  - {carrera.nombre}: {carrera.get_nombre_display()} (Unidad: {carrera.unidad_academica})")