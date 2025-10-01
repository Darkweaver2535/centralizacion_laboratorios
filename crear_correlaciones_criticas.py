#!/usr/bin/env python
"""
Script para crear correlaciones reales entre equipos, insumos y guías
"""

import os
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from guias.models import GuiaGenerada
from insumos.models import Insumo

def crear_correlaciones_criticas():
    print("=== CREANDO CORRELACIONES CRÍTICAS EQUIPOS-INSUMOS-GUÍAS ===\n")
    
    # Obtener datos existentes
    equipos = list(Equipo.objects.all())
    guias = list(GuiaGenerada.objects.all())
    insumos = list(Insumo.objects.all())
    
    print(f"📊 Datos disponibles:")
    print(f"   🔧 Equipos: {len(equipos)}")
    print(f"   📋 Guías: {len(guias)}")
    print(f"   🧪 Insumos: {len(insumos)}")
    
    if not equipos or not guias:
        print("❌ No hay suficientes datos para crear correlaciones")
        return
    
    correlaciones_creadas = 0
    
    # Crear correlaciones lógicas entre guías y equipos
    print(f"\n🔗 Creando correlaciones Guías ↔ Equipos...")
    
    for guia in guias:
        # Cada guía necesita entre 2-5 equipos aleatorios
        equipos_necesarios = random.sample(equipos, min(random.randint(2, 5), len(equipos)))
        
        for equipo in equipos_necesarios:
            guia.equipos_requeridos.add(equipo)
            correlaciones_creadas += 1
        
        print(f"   ✅ Guía '{guia.titulo}' → {len(equipos_necesarios)} equipos")
    
    # Crear correlaciones con insumos si existen
    if insumos:
        print(f"\n🧪 Creando correlaciones Guías ↔ Insumos...")
        
        for guia in guias:
            # Cada guía necesita entre 1-3 insumos
            insumos_necesarios = random.sample(insumos, min(random.randint(1, 3), len(insumos)))
            
            for insumo in insumos_necesarios:
                guia.insumos_requeridos.add(insumo)
                correlaciones_creadas += 1
            
            print(f"   ✅ Guía '{guia.titulo}' → {len(insumos_necesarios)} insumos")
    else:
        print(f"\n⚠️  No hay insumos - solo correlaciones Equipos ↔ Guías")
    
    print(f"\n📈 RESUMEN DE CORRELACIONES CREADAS:")
    print(f"   🔗 Total correlaciones: {correlaciones_creadas}")
    
    # Verificar correlaciones creadas
    print(f"\n🔍 VERIFICACIÓN DE CORRELACIONES:")
    
    for guia in guias[:3]:  # Mostrar primeras 3 guías
        equipos_count = guia.equipos_requeridos.count()
        insumos_count = guia.insumos_requeridos.count()
        print(f"   📋 {guia.titulo}:")
        print(f"      └─ Equipos requeridos: {equipos_count}")
        print(f"      └─ Insumos requeridos: {insumos_count}")
    
    # Mostrar equipos más utilizados
    from django.db.models import Count
    equipos_populares = Equipo.objects.annotate(
        uso_count=Count('guiagenerada')
    ).filter(uso_count__gt=0).order_by('-uso_count')[:5]
    
    print(f"\n🏆 EQUIPOS MÁS UTILIZADOS:")
    for equipo in equipos_populares:
        print(f"   🔧 {equipo.equipo_existente}: {equipo.uso_count} guías")
    
    print(f"\n✅ SISTEMA DE CORRELACIONES LISTO")
    print(f"🚀 Ahora se puede demostrar:")
    print(f"   • Filtrar por equipo → ver guías relacionadas")
    print(f"   • Filtrar por guía → ver equipos e insumos necesarios")
    print(f"   • Estadísticas de uso de equipos")
    print(f"   • Correlaciones en tiempo real")

if __name__ == "__main__":
    crear_correlaciones_criticas()