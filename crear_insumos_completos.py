#!/usr/bin/env python
"""
Crear insumos simplificados para correlaciones completas
Evita campos complejos como unidad_tematica_id que causan errores
"""

import os
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, Laboratorio
from insumos.models import Insumo
from guias.models import GuiaGenerada

def crear_insumos_simplificados():
    print("=== CREANDO INSUMOS SIMPLIFICADOS PARA CORRELACIONES COMPLETAS ===\n")
    
    # Obtener objetos base necesarios
    unidad_academica = UnidadAcademica.objects.first()
    carrera = Carrera.objects.first()
    asignatura = Asignatura.objects.first()
    unidad_tematica = UnidadTematica.objects.first()
    laboratorio = Laboratorio.objects.first()
    
    if not all([unidad_academica, carrera, asignatura, laboratorio]):
        print("❌ Faltan objetos base necesarios")
        return
    
    print(f"📋 Objetos base encontrados:")
    print(f"   🏫 Unidad: {unidad_academica}")
    print(f"   🎓 Carrera: {carrera}")
    print(f"   📖 Asignatura: {asignatura}")
    print(f"   🏗️ Laboratorio: {laboratorio}")
    
    # Insumos básicos para laboratorio de física
    insumos_data = [
        # Reactivos Químicos
        ('Ácido Clorhídrico 37%', 'reactivos', 'ml', 500, 50, 'Reactivo para análisis químico'),
        ('Hidróxido de Sodio', 'reactivos', 'g', 250, 25, 'Base fuerte para neutralizaciones'),
        ('Agua Destilada', 'reactivos', 'l', 5, 1, 'Disolvente para preparación de soluciones'),
        
        # Material de Vidrio
        ('Probeta Graduada 100ml', 'materiales', 'unidades', 10, 2, 'Medición de volúmenes'),
        ('Beaker 250ml', 'materiales', 'unidades', 15, 3, 'Recipiente para mezclas'),
        ('Matraz Erlenmeyer 250ml', 'materiales', 'unidades', 12, 2, 'Matraz para titulaciones'),
        ('Tubos de Ensayo', 'materiales', 'unidades', 50, 10, 'Tubos para muestras pequeñas'),
        
        # Herramientas
        ('Balanza Analítica Digital', 'herramientas', 'unidades', 2, 1, 'Pesaje de precisión'),
        ('pHmetro Digital', 'herramientas', 'unidades', 3, 1, 'Medición de pH'),
        ('Agitador Magnético', 'herramientas', 'unidades', 4, 1, 'Agitación de soluciones'),
        ('Termómetro Digital', 'herramientas', 'unidades', 8, 2, 'Medición de temperatura'),
        ('Pipetas Graduadas 10ml', 'herramientas', 'unidades', 20, 5, 'Medición precisa de volúmenes'),
    ]
    
    insumos_creados = 0
    print(f"\n🧪 Creando insumos básicos...")
    
    for nombre, categoria, unidad, cantidad, minimo, descripcion in insumos_data:
        try:
            # Crear insumo con campos mínimos requeridos
            insumo_data = {
                'nombre_elemento': nombre,
                'unidad_academica': unidad_academica,
                'laboratorio': laboratorio,
                'categoria': categoria,
                'cantidad': cantidad,
                'unidad_medida': unidad,
                'descripcion_caracteristicas': descripcion,
                'carrera': carrera,
                'asignatura': asignatura,
                'uso_principal': 'practicas',
                'condiciones_almacenamiento': 'temperatura_ambiente',
                'estado': random.choice(['bueno', 'bueno', 'regular']),  # Más buenos que regulares
            }
            
            # Agregar unidad_tematica si existe
            if unidad_tematica:
                insumo_data['unidad_tematica'] = unidad_tematica
            
            insumo, created = Insumo.objects.get_or_create(
                nombre_elemento=nombre,
                defaults=insumo_data
            )
            
            if created:
                insumos_creados += 1
                estado_emoji = "✅" if insumo.estado == "bueno" else "⚠️"
                print(f"   {estado_emoji} {nombre} ({cantidad} {unidad}) - {categoria}")
        
        except Exception as e:
            print(f"   ❌ Error creando {nombre}: {str(e)}")
    
    print(f"\n📦 Total insumos creados: {insumos_creados}")
    
    # Ahora crear correlaciones Guías ↔ Insumos
    print(f"\n🔗 Creando correlaciones Guías ↔ Insumos...")
    
    guias = GuiaGenerada.objects.all()
    insumos = list(Insumo.objects.all())
    
    correlaciones_insumos = 0
    
    for guia in guias:
        # Cada guía necesita entre 3-6 insumos aleatorios
        insumos_necesarios = random.sample(insumos, min(random.randint(3, 6), len(insumos)))
        
        for insumo in insumos_necesarios:
            guia.insumos_requeridos.add(insumo)
            correlaciones_insumos += 1
        
        print(f"   📋 {guia.titulo} → {len(insumos_necesarios)} insumos")
    
    print(f"\n📊 RESUMEN DE CORRELACIONES COMPLETAS:")
    print(f"   🔗 Correlaciones Equipos ↔ Guías: {sum(g.equipos_requeridos.count() for g in guias)}")
    print(f"   🧪 Correlaciones Insumos ↔ Guías: {correlaciones_insumos}")
    print(f"   📈 Total correlaciones: {sum(g.equipos_requeridos.count() for g in guias) + correlaciones_insumos}")
    
    # Verificar correlaciones creadas
    print(f"\n🔍 VERIFICACIÓN DE CORRELACIONES COMPLETAS:")
    for guia in guias[:2]:  # Mostrar primeras 2 guías
        equipos_count = guia.equipos_requeridos.count()
        insumos_count = guia.insumos_requeridos.count()
        print(f"   📖 {guia.titulo}:")
        print(f"      └─ Equipos: {equipos_count}")
        print(f"      └─ Insumos: {insumos_count}")
        
        # Mostrar algunos insumos
        for insumo in guia.insumos_requeridos.all()[:3]:
            estado_emoji = "✅" if insumo.estado == "bueno" else "⚠️" if insumo.estado == "regular" else "❌"
            print(f"         • {estado_emoji} {insumo.nombre_elemento} ({insumo.cantidad} {insumo.unidad_medida})")
    
    print(f"\n✅ CORRELACIONES COMPLETAS IMPLEMENTADAS")
    print(f"🎯 El sistema ahora puede demostrar:")
    print(f"   • Equipo → Guías que lo usan → Insumos necesarios")
    print(f"   • Guía → Equipos requeridos + Insumos requeridos")
    print(f"   • Insumo → Guías que lo requieren → Equipos relacionados")
    print(f"   • Círculo completo de correlaciones para presentación")

if __name__ == "__main__":
    crear_insumos_simplificados()