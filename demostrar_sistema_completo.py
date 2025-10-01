#!/usr/bin/env python
"""
Demostración de las correlaciones completas Equipos ↔ Insumos ↔ Guías
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from insumos.models import Insumo
from guias.models import GuiaGenerada

def demostrar_correlaciones_completas():
    print("=" * 70)
    print("🎯 DEMOSTRACIÓN CORRELACIONES COMPLETAS - SISTEMA R2")
    print("=" * 70)
    
    # 1. Verificar datos existentes
    total_equipos = Equipo.objects.count()
    total_insumos = Insumo.objects.count() 
    total_guias = GuiaGenerada.objects.count()
    
    print(f"\n📊 DATOS DEL SISTEMA:")
    print(f"   🔧 Total Equipos: {total_equipos}")
    print(f"   🧪 Total Insumos: {total_insumos}")
    print(f"   📋 Total Guías: {total_guias}")
    
    # 2. Demostrar correlación Equipo → Guías → Insumos
    print(f"\n🔗 DEMOSTRACIÓN: EQUIPO → GUÍAS → INSUMOS")
    print("-" * 50)
    
    # Tomar primer equipo que tenga correlaciones
    equipo_demo = Equipo.objects.filter(guiagenerada__isnull=False).first()
    if equipo_demo:
        guias_con_equipo = GuiaGenerada.objects.filter(equipos_requeridos=equipo_demo)
        
        print(f"📱 Equipo seleccionado: {equipo_demo.equipo_existente}")
        print(f"   └─ Estado: {equipo_demo.estado}")
        print(f"   └─ Laboratorio: {equipo_demo.laboratorio}")
        
        print(f"\n📋 Guías que requieren este equipo ({len(guias_con_equipo)}):")
        for guia in guias_con_equipo:
            insumos_de_guia = guia.insumos_requeridos.all()
            print(f"   • {guia.titulo}")
            print(f"     └─ Equipos totales: {guia.equipos_requeridos.count()}")
            print(f"     └─ Insumos requeridos: {insumos_de_guia.count()}")
            
            if insumos_de_guia.exists():
                for insumo in insumos_de_guia[:2]:  # Mostrar solo los primeros 2
                    print(f"        • 🧪 {insumo.nombre_elemento} ({insumo.cantidad} {insumo.unidad_medida})")
    
    # 3. Demostrar correlación Insumo → Guías → Equipos
    print(f"\n🔗 DEMOSTRACIÓN: INSUMO → GUÍAS → EQUIPOS")
    print("-" * 50)
    
    # Tomar primer insumo que tenga correlaciones
    insumo_demo = Insumo.objects.filter(guiagenerada__isnull=False).first()
    if insumo_demo:
        guias_con_insumo = GuiaGenerada.objects.filter(insumos_requeridos=insumo_demo)
        
        print(f"🧪 Insumo seleccionado: {insumo_demo.nombre_elemento}")
        print(f"   └─ Categoría: {insumo_demo.categoria}")
        print(f"   └─ Cantidad: {insumo_demo.cantidad} {insumo_demo.unidad_medida}")
        print(f"   └─ Estado: {insumo_demo.estado}")
        
        print(f"\n📋 Guías que requieren este insumo ({len(guias_con_insumo)}):")
        equipos_relacionados = set()
        
        for guia in guias_con_insumo:
            equipos_de_guia = guia.equipos_requeridos.all()
            print(f"   • {guia.titulo}")
            print(f"     └─ Equipos requeridos: {equipos_de_guia.count()}")
            print(f"     └─ Insumos totales: {guia.insumos_requeridos.count()}")
            
            # Acumular equipos relacionados
            for equipo in equipos_de_guia:
                equipos_relacionados.add(equipo)
        
        print(f"\n🔧 Equipos relacionados indirectamente con este insumo ({len(equipos_relacionados)}):")
        for equipo in list(equipos_relacionados)[:3]:  # Mostrar solo primeros 3
            print(f"   • {equipo.equipo_existente} ({equipo.estado})")
    
    # 4. Demostrar correlación Guía → Equipos + Insumos
    print(f"\n🔗 DEMOSTRACIÓN: GUÍA → EQUIPOS + INSUMOS")
    print("-" * 50)
    
    # Tomar primera guía que tenga ambos tipos de correlaciones
    guia_demo = GuiaGenerada.objects.filter(
        equipos_requeridos__isnull=False,
        insumos_requeridos__isnull=False
    ).first()
    
    if guia_demo:
        equipos_guia = guia_demo.equipos_requeridos.all()
        insumos_guia = guia_demo.insumos_requeridos.all()
        
        print(f"📋 Guía seleccionada: {guia_demo.titulo}")
        print(f"   └─ Objetivo: {guia_demo.objetivo_general[:80]}...")
        
        print(f"\n🔧 Equipos requeridos ({len(equipos_guia)}):")
        for equipo in equipos_guia[:3]:  # Mostrar primeros 3
            print(f"   • {equipo.equipo_existente}")
            print(f"     └─ Estado: {equipo.estado}")
            print(f"     └─ Laboratorio: {equipo.laboratorio}")
        
        print(f"\n🧪 Insumos requeridos ({len(insumos_guia)}):")
        for insumo in insumos_guia[:3]:  # Mostrar primeros 3
            print(f"   • {insumo.nombre_elemento}")
            print(f"     └─ Cantidad: {insumo.cantidad} {insumo.unidad_medida}")
            print(f"     └─ Estado: {insumo.estado}")
    
    # 5. Estadísticas generales de correlaciones
    print(f"\n📈 ESTADÍSTICAS GENERALES DE CORRELACIONES")
    print("-" * 50)
    
    # Equipos con correlaciones
    equipos_con_guias = Equipo.objects.filter(guiagenerada__isnull=False).distinct().count()
    porcentaje_equipos = round((equipos_con_guias / total_equipos * 100), 2) if total_equipos > 0 else 0
    
    # Insumos con correlaciones
    insumos_con_guias = Insumo.objects.filter(guiagenerada__isnull=False).distinct().count()
    porcentaje_insumos = round((insumos_con_guias / total_insumos * 100), 2) if total_insumos > 0 else 0
    
    # Guías con correlaciones
    guias_con_equipos = GuiaGenerada.objects.filter(equipos_requeridos__isnull=False).distinct().count()
    guias_con_insumos = GuiaGenerada.objects.filter(insumos_requeridos__isnull=False).distinct().count()
    guias_completas = GuiaGenerada.objects.filter(
        equipos_requeridos__isnull=False,
        insumos_requeridos__isnull=False
    ).distinct().count()
    
    print(f"📊 Utilización de recursos:")
    print(f"   🔧 Equipos utilizados: {equipos_con_guias}/{total_equipos} ({porcentaje_equipos}%)")
    print(f"   🧪 Insumos utilizados: {insumos_con_guias}/{total_insumos} ({porcentaje_insumos}%)")
    
    print(f"\n📋 Completitud de guías:")
    print(f"   • Con equipos: {guias_con_equipos}/{total_guias}")
    print(f"   • Con insumos: {guias_con_insumos}/{total_guias}") 
    print(f"   • Completas (equipos + insumos): {guias_completas}/{total_guias}")
    
    # Total de correlaciones
    total_correlaciones_equipos = sum(g.equipos_requeridos.count() for g in GuiaGenerada.objects.all())
    total_correlaciones_insumos = sum(g.insumos_requeridos.count() for g in GuiaGenerada.objects.all())
    
    print(f"\n🔗 Total correlaciones creadas:")
    print(f"   • Equipos ↔ Guías: {total_correlaciones_equipos}")
    print(f"   • Insumos ↔ Guías: {total_correlaciones_insumos}")
    print(f"   • TOTAL: {total_correlaciones_equipos + total_correlaciones_insumos}")
    
    print(f"\n✅ SISTEMA R2 LISTO PARA PRESENTACIÓN")
    print("🎯 Capacidades demostradas:")
    print("   • Correlaciones bidireccionales completas")
    print("   • Navegación entre Equipos ↔ Insumos ↔ Guías")
    print("   • Estadísticas en tiempo real")
    print("   • Filtros dinámicos jerárquicos")
    print("   • Panel de correlaciones interactivo")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    demostrar_correlaciones_completas()