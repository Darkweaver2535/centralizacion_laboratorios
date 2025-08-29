#!/usr/bin/env python3
"""
Script para redistribuir equipos a las carreras correctas según responsables y contenido
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import Carrera
from django.db import transaction

def redistribuir_equipos_carreras():
    """Redistribuir equipos a carreras correctas según responsables y contenido"""
    
    print("🔄 REDISTRIBUYENDO EQUIPOS A CARRERAS CORRECTAS")
    print("=" * 50)
    
    # Mapeo de responsables/equipos a carreras basado en análisis del Excel
    mapeo_carreras = {
        'CIVIL': ['CIVIL', 'SUELOS', 'HORMIGONES', 'RESISTENCIA', 'MATERIALES', 'ASFALTOS'],
        'SISTEMAS': ['SISTEMAS', 'COMPUTADORA', 'INFORMATICA', 'SOFTWARE', 'PROGRAMACION'],
        'INDUSTRIAL': ['INDUSTRIAL', 'PRODUCCION', 'MANUFACTURA', 'CNC', 'MAQUINA'],
        'PETROLERA': ['PETROLERA', 'PETROLEO', 'GEOLOGIA', 'PERFORACION'],
        'COMERCIAL': ['COMERCIAL', 'ADMINISTRACION', 'GESTION', 'ECONOMIA'],
    }
    
    # Mapeo específico de responsables a carreras (basado en nombres y especialidades)
    responsables_carreras = {
        'ING. ILSEN XIMENA PEREZ SHIMURA': 'ING_CIVIL',
        'ING. FRANZ ROBERTO MANCILLA ARCE': 'ING_SISTEMAS', 
        'ING. JAVIER ANGEL PAREDES VERA': 'ING_INDUSTRIAL',
        'ING. ABIGAIL NOELIA PANOZO GONZALES': 'ING_PETROLERA',
        'ING. SILVIA EUGENIA FLORES AVILA': 'ING_COMERCIAL',
        'ING. JHONATAN YUJRA TIPULA': 'ING_SISTEMAS',
        'ING. EMERSON MAMANI QUISPE': 'ING_INDUSTRIAL',
        'ING. JESSICA LIZZETH PAREDES TORREZ': 'ING_CIVIL',
        'ING. MAIRA GLADYS CALLAGUARA BAÑOS': 'ING_COMERCIAL',
        'ING.MARIANELA FLORES CONDORI': 'ING_PETROLERA',
        'ING. JHEANETE PEREZ GUZMAN': 'ING_CIVIL',
        'ING.ALISON BRITTANY LOZADA SANCHEZ': 'ING_SISTEMAS',
        'ING. MERY HILDELISA FLORES APAZA': 'ING_INDUSTRIAL',
        'ING. MARIA SUSANA ALCON QUISPE': 'ING_COMERCIAL',
    }
    
    with transaction.atomic():
        print(f"📋 Estado inicial:")
        for carrera in Carrera.objects.all():
            count = Equipo.objects.filter(carrera=carrera).count()
            print(f"   {carrera.nombre}: {count} equipos")
        
        equipos_redistribuidos = 0
        equipos_por_responsable = 0
        equipos_por_contenido = 0
        
        print(f"\n🔧 Redistribuyendo por responsable...")
        
        # 1. Redistribuir por responsable específico
        for responsable, carrera_codigo in responsables_carreras.items():
            try:
                carrera = Carrera.objects.get(nombre=carrera_codigo)
                equipos = Equipo.objects.filter(responsable_excel=responsable)
                count = equipos.count()
                
                if count > 0:
                    equipos.update(carrera=carrera)
                    equipos_redistribuidos += count
                    equipos_por_responsable += count
                    print(f"   ✅ {responsable[:30]}... → {carrera_codigo}: {count} equipos")
                    
            except Carrera.DoesNotExist:
                print(f"   ❌ Carrera {carrera_codigo} no encontrada")
        
        # 2. Redistribuir equipos restantes por contenido
        print(f"\n🔍 Redistribuyendo por contenido del equipo...")
        
        equipos_sin_responsable = Equipo.objects.filter(responsable_excel__isnull=True) | Equipo.objects.filter(responsable_excel='')
        
        for equipo in equipos_sin_responsable[:50]:  # Procesar muestra
            equipo_texto = f"{equipo.equipo_existente} {equipo.marca} {equipo.modelo}".upper()
            
            carrera_asignada = None
            for carrera_nombre, palabras_clave in mapeo_carreras.items():
                for palabra in palabras_clave:
                    if palabra in equipo_texto:
                        try:
                            carrera_asignada = Carrera.objects.get(nombre=f'ING_{carrera_nombre}')
                            break
                        except Carrera.DoesNotExist:
                            continue
                if carrera_asignada:
                    break
            
            if carrera_asignada and carrera_asignada != equipo.carrera:
                equipo.carrera = carrera_asignada
                equipo.save()
                equipos_redistribuidos += 1
                equipos_por_contenido += 1
                if equipos_por_contenido <= 10:  # Mostrar primeros 10
                    print(f"   ✅ {equipo.equipo_existente[:40]}... → {carrera_asignada.nombre}")
        
        print(f"\n📊 RESUMEN DE REDISTRIBUCIÓN:")
        print(f"✅ Total redistribuidos: {equipos_redistribuidos}")
        print(f"👤 Por responsable: {equipos_por_responsable}")
        print(f"🔍 Por contenido: {equipos_por_contenido}")
        
        print(f"\n📊 DISTRIBUCIÓN FINAL:")
        for carrera in Carrera.objects.all():
            count = Equipo.objects.filter(carrera=carrera).count()
            if count > 0:
                print(f"   📚 {carrera.nombre}: {count:,} equipos")
                
                # Mostrar responsables principales
                responsables = Equipo.objects.filter(carrera=carrera).values_list('responsable_excel', flat=True).distinct()
                responsables_list = [r for r in responsables if r][:3]
                for resp in responsables_list:
                    resp_count = Equipo.objects.filter(carrera=carrera, responsable_excel=resp).count()
                    print(f"       👤 {resp}: {resp_count} equipos")

if __name__ == "__main__":
    redistribuir_equipos_carreras()
