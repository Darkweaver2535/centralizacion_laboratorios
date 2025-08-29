#!/usr/bin/env python3
"""
Verificación final: estados oficiales en filtros de visualización
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo

def verificar_filtros_estados():
    """Verificar que los filtros muestren solo los 3 estados oficiales"""
    
    print("🔍 VERIFICACIÓN FINAL: FILTROS DE ESTADOS")
    print("=" * 45)
    
    # Estados del modelo
    print("📋 ESTADOS DISPONIBLES EN EL MODELO:")
    for codigo, nombre in Equipo.ESTADOS:
        count = Equipo.objects.filter(estado=codigo).count()
        print(f"   {codigo} → {nombre} ({count:,} equipos)")
    
    # Verificar que solo existen los 3 estados oficiales
    estados_esperados = {'bueno', 'regular', 'malo'}
    estados_en_bd = set(Equipo.objects.values_list('estado', flat=True).distinct())
    
    print(f"\n🎯 VERIFICACIÓN DE CONSISTENCIA:")
    print(f"   Estados esperados: {estados_esperados}")
    print(f"   Estados en BD: {estados_en_bd}")
    
    if estados_en_bd == estados_esperados:
        print("   ✅ PERFECTO: Solo existen los 3 estados oficiales")
    else:
        estados_extra = estados_en_bd - estados_esperados
        estados_faltantes = estados_esperados - estados_en_bd
        if estados_extra:
            print(f"   ❌ Estados extra: {estados_extra}")
        if estados_faltantes:
            print(f"   ❌ Estados faltantes: {estados_faltantes}")
    
    print(f"\n📊 RESUMEN PARA FILTROS:")
    total = Equipo.objects.count()
    for estado in ['bueno', 'regular', 'malo']:
        count = Equipo.objects.filter(estado=estado).count()
        porcentaje = (count / total * 100) if total > 0 else 0
        emoji = {'bueno': '✅', 'regular': '⚠️', 'malo': '❌'}[estado]
        print(f"   {emoji} {estado.capitalize()}: {count:,} equipos ({porcentaje:.1f}%)")
    
    print(f"\n🚀 Los filtros ahora deben mostrar solo 3 opciones:")
    print(f"   1. Bueno")
    print(f"   2. Regular") 
    print(f"   3. Malo")

if __name__ == "__main__":
    verificar_filtros_estados()
