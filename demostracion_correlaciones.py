#!/usr/bin/env python
"""
Demostración completa del Sistema de Correlaciones R2
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from guias.models import GuiaGenerada
from django.db.models import Count

def demostracion_correlaciones():
    print("=" * 70)
    print("🚀 DEMOSTRACIÓN DEL SISTEMA DE CORRELACIONES R2")
    print("=" * 70)
    
    print(f"\n📊 DATOS BASE DEL SISTEMA:")
    print(f"   🔧 Equipos totales: {Equipo.objects.count()}")
    print(f"   📋 Guías totales: {GuiaGenerada.objects.count()}")
    
    print(f"\n🔗 CORRELACIONES ACTIVAS:")
    
    # Mostrar equipos con más correlaciones
    equipos_populares = Equipo.objects.annotate(
        uso_count=Count('guiagenerada')
    ).filter(uso_count__gt=0).order_by('-uso_count')[:5]
    
    print(f"   🏆 TOP 5 EQUIPOS MÁS UTILIZADOS:")
    for i, equipo in enumerate(equipos_populares, 1):
        guias_relacionadas = GuiaGenerada.objects.filter(equipos_requeridos=equipo)
        print(f"      {i}. {equipo.equipo_existente} → {equipo.uso_count} guías")
        for guia in guias_relacionadas[:2]:  # Mostrar primeras 2 guías
            print(f"         └─ {guia.titulo}")
    
    print(f"\n📋 GUÍAS CON CORRELACIONES:")
    guias_con_equipos = GuiaGenerada.objects.filter(equipos_requeridos__isnull=False).distinct()
    
    for guia in guias_con_equipos:
        equipos_count = guia.equipos_requeridos.count()
        print(f"   📖 {guia.titulo}:")
        print(f"      └─ Requiere {equipos_count} equipos")
        
        # Mostrar algunos equipos
        for equipo in guia.equipos_requeridos.all()[:3]:
            estado_emoji = "✅" if equipo.estado == "bueno" else "⚠️" if equipo.estado == "regular" else "❌"
            print(f"         • {estado_emoji} {equipo.equipo_existente} ({equipo.estado})")
    
    print(f"\n🌐 ENDPOINTS DISPONIBLES PARA CORRELACIONES:")
    print(f"   • /visualizacion/ajax/correlaciones-equipo/?equipo_id=X")
    print(f"   • /visualizacion/ajax/correlaciones-guia/?guia_id=X") 
    print(f"   • /visualizacion/ajax/resumen-correlaciones/")
    
    print(f"\n📊 ESTADÍSTICAS DE CORRELACIONES:")
    total_correlaciones = 0
    for guia in GuiaGenerada.objects.all():
        total_correlaciones += guia.equipos_requeridos.count()
    
    equipos_utilizados = Equipo.objects.filter(guiagenerada__isnull=False).distinct().count()
    porcentaje_uso = (equipos_utilizados / Equipo.objects.count() * 100) if Equipo.objects.count() > 0 else 0
    
    print(f"   🔗 Total correlaciones creadas: {total_correlaciones}")
    print(f"   🎯 Equipos utilizados: {equipos_utilizados}/{Equipo.objects.count()} ({porcentaje_uso:.1f}%)")
    print(f"   📚 Guías con equipos: {guias_con_equipos.count()}/{GuiaGenerada.objects.count()}")
    
    print(f"\n✅ EJEMPLO DE USO DEL SISTEMA:")
    print(f"   1. 👤 Usuario selecciona categoria 'equipos'")
    print(f"   2. 🔍 Aplica filtros dinámicos (Unidad → Carrera → Semestre)")
    print(f"   3. 🖱️  Hace clic en un equipo específico")
    print(f"   4. 🔗 Sistema muestra TODAS las guías que requieren ese equipo")
    print(f"   5. 📊 Actualiza estadísticas de uso en tiempo real")
    print(f"   6. 🎯 Permite navegación inversa: Guía → Equipos requeridos")
    
    print(f"\n" + "=" * 70)
    print(f"💡 SISTEMA DE CORRELACIONES R2 COMPLETAMENTE FUNCIONAL")
    print(f"🎯 LISTO PARA PRESENTACIÓN DEL 2 DE OCTUBRE")
    print(f"🌐 URL: http://127.0.0.1:8000/visualizacion/?categoria=equipos")
    print(f"=" * 70)

if __name__ == "__main__":
    demostracion_correlaciones()