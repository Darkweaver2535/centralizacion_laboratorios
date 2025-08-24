#!/usr/bin/env python
"""
Script para corregir las carreras con las 18 carreras OFICIALES correctas de EMI
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera
from django.db import transaction

def limpiar_y_crear_carreras_oficiales():
    """Limpia las carreras existentes y crea las 18 carreras OFICIALES de EMI"""
    
    print("🧹 Limpiando carreras existentes...")
    
    with transaction.atomic():
        # Eliminar todas las carreras existentes
        count_eliminadas = Carrera.objects.all().count()
        Carrera.objects.all().delete()
        print(f"  ✅ Eliminadas {count_eliminadas} carreras antiguas")
        
        # Las 18 carreras OFICIALES de EMI - TODAS para TODAS las unidades
        carreras_oficiales = [
            ('ING_CIVIL', 'Ingeniería Civil'),
            ('ING_GEOGRAFICA', 'Ingeniería Geográfica'),
            ('ING_SISTEMAS_ELECTRONICOS', 'Ingeniería en Sistemas Electrónicos'),
            ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
            ('ING_COMERCIAL', 'Ingeniería Comercial'),
            ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
            ('ING_AMBIENTAL', 'Ingeniería Ambiental'),
            ('ING_PETROLERA', 'Ingeniería Petrolera'),
            ('ING_MECATRONICA', 'Ingeniería Mecatrónica'),
            ('ING_TELECOMUNICACIONES', 'Ingeniería en Telecomunicaciones'),
            ('ING_FINANCIERA', 'Ingeniería Financiera'),
            ('ING_AGROINDUSTRIAL', 'Ingeniería Agroindustrial'),
            ('ING_AGRONOMICA', 'Ingeniería Agronómica'),
            ('INFORMATICA', 'Informática'),
            ('SISTEMAS_ELECTRONICOS', 'Sistemas Electrónicos'),
            ('ENERGIAS_RENOVABLES', 'Energías Renovables'),
            ('CONSTRUCCION_CIVIL', 'Construcción Civil'),
            ('DISENO_GRAFICO', 'Diseño Gráfico y Comunicación Audiovisual'),
        ]
        
        # TODAS las carreras para TODAS las unidades académicas
        unidades = UnidadAcademica.objects.all()
        
        total_creadas = 0
        
        print(f"\n📚 Creando las 18 CARRERAS OFICIALES para TODAS las unidades:")
        for unidad in unidades:
            print(f"\n  🏛️  {unidad.nombre} ({unidad.get_nombre_display()}):")
            
            for carrera_codigo, carrera_nombre in carreras_oficiales:
                carrera, created = Carrera.objects.get_or_create(
                    unidad_academica=unidad,
                    nombre=carrera_codigo,
                    defaults={'descripcion': carrera_nombre}
                )
                if created:
                    print(f"    ✅ {carrera_nombre}")
                    total_creadas += 1
                else:
                    print(f"    ℹ️  {carrera_nombre} (ya existía)")
        
        print(f"\n🎯 Total de carreras creadas: {total_creadas}")
        print(f"📊 Carreras OFICIALES EMI: {len(carreras_oficiales)}")
        print(f"🏛️  Unidades académicas: {unidades.count()}")
        print(f"🔢 Total esperado: {len(carreras_oficiales)} × {unidades.count()} = {len(carreras_oficiales) * unidades.count()}")

def verificar_carreras_oficiales():
    """Verifica que solo existan las carreras oficiales"""
    print("\n🔍 VERIFICACIÓN DE CARRERAS OFICIALES EMI:")
    print("=" * 50)
    
    # Lista de carreras oficiales
    carreras_oficiales_nombres = [
        'Ingeniería Civil',
        'Ingeniería Geográfica',
        'Ingeniería en Sistemas Electrónicos',
        'Ingeniería Industrial',
        'Ingeniería Comercial',
        'Ingeniería de Sistemas',
        'Ingeniería Ambiental',
        'Ingeniería Petrolera',
        'Ingeniería Mecatrónica',
        'Ingeniería en Telecomunicaciones',
        'Ingeniería Financiera',
        'Ingeniería Agroindustrial',
        'Ingeniería Agronómica',
        'Informática',
        'Sistemas Electrónicos',
        'Energías Renovables',
        'Construcción Civil',
        'Diseño Gráfico y Comunicación Audiovisual'
    ]
    
    unidades = UnidadAcademica.objects.all().order_by('nombre')
    total_carreras = 0
    
    for unidad in unidades:
        carreras = Carrera.objects.filter(unidad_academica=unidad)
        count = carreras.count()
        total_carreras += count
        
        print(f"\n🏛️  {unidad.nombre} ({unidad.get_nombre_display()}):")
        print(f"   📚 Total de carreras: {count}")
        
        if count > 0:
            for carrera in carreras.order_by('nombre'):
                nombre_display = carrera.get_nombre_display()
                if nombre_display in carreras_oficiales_nombres:
                    print(f"   ✅ {nombre_display}")
                else:
                    print(f"   ❌ {nombre_display} (NO OFICIAL)")
        else:
            print("   ⚠️  Sin carreras asignadas")
    
    print(f"\n📊 RESUMEN: {total_carreras} carreras en {unidades.count()} unidades")
    print(f"🎯 OBJETIVO: 18 carreras oficiales EMI")

if __name__ == "__main__":
    print("🎓 TODAS LAS 18 CARRERAS OFICIALES PARA TODAS LAS UNIDADES")
    print("📍 Cada unidad académica tendrá las 18 carreras disponibles")
    print("=" * 65)
    
    # Limpiar y recrear carreras OFICIALES
    limpiar_y_crear_carreras_oficiales()
    
    # Verificar resultado
    verificar_carreras_oficiales()
    
    print("\n✅ CORRECCIÓN COMPLETADA")
    print("💡 Las 18 carreras OFICIALES están disponibles en TODAS las unidades")
    print("� Después se pueden separar por unidad según necesidades específicas")
    print("🚀 Sistema completo y funcional")
