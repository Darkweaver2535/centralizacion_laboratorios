#!/usr/bin/env python3
"""
Script para actualizar los estados de equipos a los tres oficiales: bueno, regular, malo
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from django.db import transaction
from django.db.models import Count

def actualizar_estados_equipos():
    """Actualizar estados de equipos a los tres oficiales"""
    
    print("🔧 ACTUALIZANDO ESTADOS DE EQUIPOS A VALORES OFICIALES")
    print("=" * 55)
    
    # Mapeo de estados antiguos a nuevos
    mapeo_estados = {
        'operativo': 'bueno',
        'nuevo': 'bueno',
        'usado': 'regular',
        'mantenimiento': 'regular',
        'necesita_mantenimiento': 'regular',
        'reparacion': 'malo',
        'inoperativo': 'malo',
        'fuera_servicio': 'malo',
        'descartado': 'malo',
    }
    
    with transaction.atomic():
        print(f"📋 Estado inicial:")
        total_equipos = Equipo.objects.count()
        print(f"   Total de equipos: {total_equipos}")
        
        # Mostrar distribución actual
        print(f"\n📊 Distribución actual de estados:")
        estados_actuales = Equipo.objects.values('estado').annotate(
            total=Count('id')
        ).order_by('-total')
        
        for item in estados_actuales:
            estado = item['estado']
            total = item['total']
            porcentaje = (total / total_equipos * 100) if total_equipos > 0 else 0
            print(f"   {estado}: {total} equipos ({porcentaje:.1f}%)")
        
        print(f"\n🔄 Actualizando estados...")
        equipos_actualizados = 0
        
        for estado_antiguo, estado_nuevo in mapeo_estados.items():
            equipos_con_estado = Equipo.objects.filter(estado=estado_antiguo)
            count = equipos_con_estado.count()
            
            if count > 0:
                equipos_con_estado.update(estado=estado_nuevo)
                equipos_actualizados += count
                print(f"   ✅ {estado_antiguo} → {estado_nuevo}: {count} equipos")
        
        # Equipos que ya tienen estados válidos
        estados_validos = ['bueno', 'regular', 'malo']
        equipos_ya_validos = Equipo.objects.filter(estado__in=estados_validos).count()
        
        print(f"\n📊 RESUMEN:")
        print(f"✅ Equipos actualizados: {equipos_actualizados}")
        print(f"✅ Equipos ya válidos: {equipos_ya_validos}")
        print(f"📋 Total procesado: {equipos_actualizados + equipos_ya_validos}")
        
        # Distribución final
        print(f"\n🎯 DISTRIBUCIÓN FINAL DE ESTADOS:")
        estados_finales = Equipo.objects.values('estado').annotate(
            total=Count('id')
        ).order_by('estado')
        
        for item in estados_finales:
            estado = item['estado']
            total = item['total']
            porcentaje = (total / total_equipos * 100) if total_equipos > 0 else 0
            
            # Emojis para cada estado
            emoji = {
                'bueno': '✅',
                'regular': '⚠️',
                'malo': '❌'
            }.get(estado, '❓')
            
            print(f"   {emoji} {estado.capitalize()}: {total} equipos ({porcentaje:.1f}%)")
        
        # Verificar que no hay estados inválidos
        equipos_invalidos = Equipo.objects.exclude(estado__in=estados_validos).count()
        if equipos_invalidos > 0:
            print(f"\n⚠️ ADVERTENCIA: {equipos_invalidos} equipos con estados no válidos")
        else:
            print(f"\n✅ ÉXITO: Todos los equipos tienen estados válidos")

if __name__ == "__main__":
    actualizar_estados_equipos()
