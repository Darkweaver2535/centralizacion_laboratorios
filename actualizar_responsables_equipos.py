#!/usr/bin/env python3
"""
Script para actualizar los equipos con los nombres de responsables del Excel
"""

import os
import sys
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from django.db import transaction

def actualizar_responsables_equipos():
    """Actualizar equipos con nombres de responsables del Excel"""
    
    print("🔄 ACTUALIZANDO RESPONSABLES EN EQUIPOS")
    print("=" * 50)
    
    # Leer Excel para obtener mapping de responsables
    print("📊 Leyendo datos del Excel...")
    df = pd.read_excel('pruebas/completo.xlsx')
    
    # Crear un mapping de código -> responsable
    responsables_mapping = {}
    for _, row in df.iterrows():
        codigo = str(row.get('CODIGO', '')).strip()
        responsable = str(row.get('RESPONSABLE', '')).strip()
        if codigo and responsable:
            responsables_mapping[codigo] = responsable
    
    print(f"📋 Encontrados {len(responsables_mapping)} códigos con responsables")
    
    # Actualizar equipos
    with transaction.atomic():
        equipos_actualizados = 0
        equipos_sin_codigo = 0
        equipos_sin_responsable = 0
        
        for equipo in Equipo.objects.all():
            if equipo.codigo_inventario:
                # Buscar responsable por código de inventario
                responsable = responsables_mapping.get(equipo.codigo_inventario)
                if responsable:
                    equipo.responsable_excel = responsable
                    equipo.save()
                    equipos_actualizados += 1
                    print(f"✅ Equipo {equipo.codigo_inventario}: {responsable[:50]}...")
                else:
                    equipos_sin_responsable += 1
                    print(f"⚠️  Sin responsable: {equipo.codigo_inventario}")
            else:
                equipos_sin_codigo += 1
        
        print(f"\n📊 RESUMEN DE ACTUALIZACIÓN:")
        print(f"✅ Equipos actualizados: {equipos_actualizados}")
        print(f"⚠️  Equipos sin código: {equipos_sin_codigo}")
        print(f"❌ Equipos sin responsable: {equipos_sin_responsable}")
        print(f"📋 Total equipos: {Equipo.objects.count()}")
        
        # Mostrar estadísticas de responsables
        print(f"\n👥 RESPONSABLES MÁS FRECUENTES:")
        responsables_stats = {}
        for equipo in Equipo.objects.exclude(responsable_excel=''):
            resp = equipo.responsable_excel
            responsables_stats[resp] = responsables_stats.get(resp, 0) + 1
        
        for responsable, count in sorted(responsables_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {count:3d} equipos: {responsable}")

if __name__ == "__main__":
    actualizar_responsables_equipos()
