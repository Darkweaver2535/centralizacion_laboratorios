#!/usr/bin/env python3
"""
Script para actualizar los laboratorios según los datos reales del Excel
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Laboratorio
from django.db import transaction

def actualizar_laboratorios():
    """Actualizar laboratorios según datos reales del Excel de materiales"""
    
    print("🔬 ACTUALIZANDO LABORATORIOS SEGÚN EXCEL DE MATERIALES")
    print("=" * 55)
    
    # Laboratorios del Excel de recopilación de materiales
    laboratorios_excel = [
        ('LAB_TRATAMIENTO_AGUAS', 'Planta de Tratamiento de Aguas'),
        ('LAB_ASFALTOS', 'Laboratorio de Asfaltos'),
        ('LAB_HORMIGONES', 'Laboratorio de Hormigones'),
        ('LAB_RESISTENCIA_MATERIALES', 'Laboratorio de Resistencia de Materiales y Suelos'),
        ('LAB_LACTEOS', 'Laboratorio de Lácteos'),
    ]
    
    # Laboratorios adicionales para completar la lista
    laboratorios_adicionales = [
        ('LAB_FISICA_1', 'Laboratorio de Física Piso 1'),
        ('LAB_FISICA_4', 'Laboratorio de Física Piso 4'),
        ('LAB_QUIMICA', 'Laboratorio de Química General'),
        ('LAB_BIOTECNOLOGIA', 'Laboratorio de Biotecnología'),
        ('LAB_SISTEMAS_1', 'Laboratorio de Sistemas Piso 1'),
        ('LAB_SISTEMAS_I', 'Laboratorio de Sistemas I'),
        ('LAB_MECATRONICA', 'Laboratorio de Mecatrónica'),
        ('LAB_INDUSTRIAL', 'Laboratorio Industrial'),
        ('LAB_CIVIL', 'Laboratorio de Civil'),
        ('LAB_PETROLERA', 'Laboratorio Petrolero y Geográfico'),
        ('OFICINAS_UICYT', 'Oficinas Unidad de Investigación'),
    ]
    
    todos_laboratorios = laboratorios_excel + laboratorios_adicionales
    
    with transaction.atomic():
        print(f"📋 Estado inicial:")
        print(f"   Laboratorios en BD: {Laboratorio.objects.count()}")
        
        laboratorios_creados = 0
        laboratorios_existentes = 0
        
        print(f"\n🔧 Procesando laboratorios...")
        
        for codigo, nombre_display in todos_laboratorios:
            try:
                laboratorio = Laboratorio.objects.get(nombre=codigo)
                laboratorios_existentes += 1
                print(f"✅ Existente: {nombre_display}")
            except Laboratorio.DoesNotExist:
                laboratorio = Laboratorio.objects.create(
                    nombre=codigo,
                    descripcion=f'Laboratorio especializado: {nombre_display}',
                    ubicacion='UACB - Universidad Autónoma del Beni',
                    capacidad=25
                )
                laboratorios_creados += 1
                print(f"🆕 Creado: {nombre_display}")
        
        print(f"\n📊 RESUMEN:")
        print(f"✅ Laboratorios existentes: {laboratorios_existentes}")
        print(f"🆕 Laboratorios creados: {laboratorios_creados}")
        print(f"📋 Total laboratorios: {Laboratorio.objects.count()}")
        
        print(f"\n🔬 LABORATORIOS PRINCIPALES DEL EXCEL:")
        for codigo, nombre in laboratorios_excel:
            print(f"  ⭐ {nombre}")
            
        print(f"\n🏗️ LABORATORIOS ADICIONALES:")
        for codigo, nombre in laboratorios_adicionales:
            print(f"  + {nombre}")
        
        print(f"\n📍 LISTA COMPLETA EN SISTEMA:")
        for i, lab in enumerate(Laboratorio.objects.all().order_by('nombre'), 1):
            print(f"  {i:2d}. {lab.get_nombre_display()}")

if __name__ == "__main__":
    actualizar_laboratorios()
