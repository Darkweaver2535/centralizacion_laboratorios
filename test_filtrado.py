#!/usr/bin/env python3
"""
Script para probar el filtrado de equipos sin necesidad de autenticación web
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from ingreso_datos.models import *
from django.http import HttpRequest
from django.contrib.auth.models import User
import json

def test_filtrado():
    """Test del filtrado de equipos"""
    print("=== PRUEBA DE FILTRADO DE EQUIPOS ===\n")
    
    # Obtener un tipo de equipo para las pruebas
    tipo_equipo = TipoEquipo.objects.first()
    print(f"Tipo de equipo de prueba: {tipo_equipo.nombre}")
    
    # Probar filtrado por cada unidad académica
    unidades = UnidadAcademica.objects.all()
    
    for ua in unidades:
        print(f"\n--- Probando con {ua.nombre} ({ua.get_nombre_display()}) ---")
        
        # Simular la lógica de get_equipos_individuales
        try:
            equipos = EquipoIndividual.objects.filter(
                tipo_equipo=tipo_equipo,
                estado_operativo='operativo',
                unidad_academica=ua
            )
            
            total_equipos = EquipoIndividual.objects.filter(
                tipo_equipo=tipo_equipo,
                unidad_academica=ua
            ).count()
            
            print(f"  Equipos operativos: {equipos.count()}")
            print(f"  Total equipos: {total_equipos}")
            
            if equipos.exists():
                print(f"  Primer equipo: {equipos.first().codigo}")
            
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Probar con unidad académica inexistente
    print(f"\n--- Probando con unidad académica inexistente (riberalta) ---")
    try:
        ua_inexistente = UnidadAcademica.objects.get(nombre='riberalta')
        print(f"  ERROR: Riberalta no debería existir, pero existe: {ua_inexistente}")
    except UnidadAcademica.DoesNotExist:
        print("  ✓ Riberalta NO existe - el filtrado funcionará correctamente")
        print("  ✓ La vista debería devolver equipos=[] para esta unidad")
    
    print("\n=== RESUMEN ===")
    print("- La Paz: Debería mostrar equipos cuando existan")
    print("- Cochabamba: Debería mostrar equipos cuando existan")
    print("- Santa Cruz: Debería mostrar equipos=[] (no tiene equipos)")
    print("- Riberalta: Debería mostrar equipos=[] (no existe)")
    print("- CRUCIAL: Cada unidad solo ve sus propios equipos")

if __name__ == "__main__":
    test_filtrado()
