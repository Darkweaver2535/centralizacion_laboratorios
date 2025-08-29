#!/usr/bin/env python3
"""
Script para redistribuir equipos a laboratorios según datos del Excel
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Laboratorio
from equipos.models import Equipo
from django.db import transaction

def redistribuir_equipos_laboratorios():
    """Redistribuir equipos a laboratorios correctos según datos del Excel"""
    
    print("🔄 REDISTRIBUYENDO EQUIPOS A LABORATORIOS CORRECTOS")
    print("=" * 55)
    
    # Mapeo de nombres/palabras clave a laboratorios
    mapeo_laboratorios = {
        # Laboratorios principales del Excel
        'ASFALTOS': 'LAB_ASFALTOS',
        'HORMIGONES': 'LAB_HORMIGONES', 
        'HORMIGÓN': 'LAB_HORMIGONES',
        'RESISTENCIA': 'LAB_RESISTENCIA_MATERIALES',
        'MATERIALES': 'LAB_RESISTENCIA_MATERIALES',
        'SUELOS': 'LAB_RESISTENCIA_MATERIALES',
        'LÁCTEOS': 'LAB_LACTEOS',
        'LACTEOS': 'LAB_LACTEOS',
        'TRATAMIENTO': 'LAB_TRATAMIENTO_AGUAS',
        'AGUAS': 'LAB_TRATAMIENTO_AGUAS',
        
        # Laboratorios adicionales
        'BIOTECNOLOGÍA': 'LAB_BIOTECNOLOGIA',
        'BIOTECNOLOGIA': 'LAB_BIOTECNOLOGIA',
        'QUÍMICA': 'LAB_QUIMICA',
        'QUIMICA': 'LAB_QUIMICA',
        'CIVIL': 'LAB_CIVIL',
        'FÍSICA': 'LAB_FISICA_1',
        'FISICA': 'LAB_FISICA_1',
        'SISTEMAS': 'LAB_SISTEMAS_1',
        'MECATRÓNICA': 'LAB_MECATRONICA',
        'MECATRONICA': 'LAB_MECATRONICA',
        'INDUSTRIAL': 'LAB_INDUSTRIAL',
        'PETROLERO': 'LAB_PETROLERA',
        'PETROLEO': 'LAB_PETROLERA',
    }
    
    with transaction.atomic():
        print(f"📋 Estado inicial:")
        lab_ualp = Laboratorio.objects.get(nombre='Laboratorio UALP')
        equipos_ualp = Equipo.objects.filter(laboratorio=lab_ualp).count()
        print(f"   Equipos en Laboratorio UALP: {equipos_ualp}")
        
        equipos_redistribuidos = 0
        equipos_sin_reasignar = 0
        
        print(f"\n🔧 Analizando equipos por nombre y descripción...")
        
        # Obtener todos los equipos del Laboratorio UALP
        equipos = Equipo.objects.filter(laboratorio=lab_ualp)
        
        for equipo in equipos:
            nuevo_laboratorio = None
            
            # Buscar por nombre del equipo
            equipo_existente_upper = equipo.equipo_existente.upper() if equipo.equipo_existente else ''
            marca_upper = equipo.marca.upper() if equipo.marca else ''
            modelo_upper = equipo.modelo.upper() if equipo.modelo else ''
            texto_completo = f"{equipo_existente_upper} {marca_upper} {modelo_upper}"
            
            for palabra_clave, lab_codigo in mapeo_laboratorios.items():
                if palabra_clave in texto_completo:
                    try:
                        nuevo_laboratorio = Laboratorio.objects.get(nombre=lab_codigo)
                        break
                    except Laboratorio.DoesNotExist:
                        continue
            
            # Si no se encontró por nombre/descripción, usar responsable como indicativo
            if not nuevo_laboratorio and equipo.responsable_excel:
                responsable_upper = equipo.responsable_excel.upper()
                
                # Mapeo básico por especialidad del responsable
                if 'CIVIL' in responsable_upper:
                    try:
                        nuevo_laboratorio = Laboratorio.objects.get(nombre='LAB_CIVIL')
                    except Laboratorio.DoesNotExist:
                        pass
                elif 'QUIMICA' in responsable_upper or 'QUÍMICA' in responsable_upper:
                    try:
                        nuevo_laboratorio = Laboratorio.objects.get(nombre='LAB_QUIMICA')
                    except Laboratorio.DoesNotExist:
                        pass
                elif 'SISTEMAS' in responsable_upper:
                    try:
                        nuevo_laboratorio = Laboratorio.objects.get(nombre='LAB_SISTEMAS_1')
                    except Laboratorio.DoesNotExist:
                        pass
            
            # Asignar laboratorio si se encontró uno apropiado
            if nuevo_laboratorio:
                equipo.laboratorio = nuevo_laboratorio
                equipo.save()
                equipos_redistribuidos += 1
                if equipos_redistribuidos <= 10:  # Mostrar solo primeros 10
                    print(f"  ✅ {equipo.equipo_existente[:50]}... → {nuevo_laboratorio.get_nombre_display()}")
            else:
                equipos_sin_reasignar += 1
        
        print(f"\n📊 RESUMEN DE REDISTRIBUCIÓN:")
        print(f"✅ Equipos redistribuidos: {equipos_redistribuidos}")
        print(f"⚪ Equipos sin reasignar: {equipos_sin_reasignar}")
        
        # Estadísticas finales
        print(f"\n📍 DISTRIBUCIÓN FINAL POR LABORATORIO:")
        for lab in Laboratorio.objects.all().order_by('nombre'):
            count = Equipo.objects.filter(laboratorio=lab).count()
            if count > 0:
                print(f"  📍 {lab.get_nombre_display()}: {count} equipos")

if __name__ == "__main__":
    redistribuir_equipos_laboratorios()
