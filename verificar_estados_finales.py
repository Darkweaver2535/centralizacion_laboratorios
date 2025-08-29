#!/usr/bin/env python3
"""
Script para verificar que los estados oficiales estén funcionando correctamente
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from django.db.models import Count

def verificar_estados_finales():
    """Verificar que los estados oficiales estén funcionando"""
    
    print("✅ VERIFICACIÓN FINAL DE ESTADOS OFICIALES")
    print("=" * 45)
    
    total_equipos = Equipo.objects.count()
    print(f"📋 Total de equipos: {total_equipos}")
    
    # Verificar los tres estados oficiales
    estados_oficiales = ['bueno', 'regular', 'malo']
    
    print(f"\n🎯 ESTADOS OFICIALES DISPONIBLES:")
    for estado_codigo, estado_display in Equipo.ESTADOS:
        print(f"   {estado_codigo} → {estado_display}")
    
    print(f"\n📊 DISTRIBUCIÓN ACTUAL:")
    for estado in estados_oficiales:
        count = Equipo.objects.filter(estado=estado).count()
        porcentaje = (count / total_equipos * 100) if total_equipos > 0 else 0
        
        emoji = {
            'bueno': '✅',
            'regular': '⚠️',
            'malo': '❌'
        }[estado]
        
        print(f"   {emoji} {estado.capitalize()}: {count:,} equipos ({porcentaje:.1f}%)")
    
    # Verificar que no hay estados inválidos
    equipos_invalidos = Equipo.objects.exclude(estado__in=estados_oficiales)
    if equipos_invalidos.exists():
        print(f"\n❌ PROBLEMA: {equipos_invalidos.count()} equipos con estados no válidos")
        for estado_invalido in equipos_invalidos.values_list('estado', flat=True).distinct():
            count = equipos_invalidos.filter(estado=estado_invalido).count()
            print(f"     - {estado_invalido}: {count} equipos")
    else:
        print(f"\n✅ PERFECTO: Todos los equipos tienen estados válidos")
    
    # Verificar filtros
    print(f"\n🔍 VERIFICACIÓN DE FILTROS:")
    print(f"   Equipos en estado 'bueno': {Equipo.objects.filter(estado='bueno').count()}")
    print(f"   Equipos en estado 'regular': {Equipo.objects.filter(estado='regular').count()}")
    print(f"   Equipos en estado 'malo': {Equipo.objects.filter(estado='malo').count()}")
    
    print(f"\n🚀 SISTEMA LISTO PARA USO CON ESTADOS OFICIALES")

if __name__ == "__main__":
    verificar_estados_finales()
