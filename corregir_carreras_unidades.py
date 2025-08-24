#!/usr/bin/env python
"""
Script para corregir las carreras con las nuevas unidades académicas oficiales
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera
from django.db import transaction

def limpiar_y_crear_carreras():
    """Limpia las carreras existentes y crea nuevas con las unidades académicas oficiales"""
    
    print("🧹 Limpiando carreras existentes...")
    
    with transaction.atomic():
        # Eliminar todas las carreras existentes
        count_eliminadas = Carrera.objects.all().count()
        Carrera.objects.all().delete()
        print(f"  ✅ Eliminadas {count_eliminadas} carreras antiguas")
        
        # Crear carreras para cada unidad académica
        carreras_por_unidad = {
            'UALP': [
                ('ING_CIVIL', 'Ingeniería Civil'),
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('MEDICINA', 'Medicina'),
                ('ENFERMERIA', 'Enfermería'),
                ('DERECHO', 'Derecho'),
            ],
            'UASC': [
                ('ING_CIVIL', 'Ingeniería Civil'),
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
                ('ING_MECANICA', 'Ingeniería Mecánica'),
                ('ING_MECATRONICA', 'Ingeniería Mecatrónica'),
                ('ING_PETROLERA', 'Ingeniería Petrolera'),
                ('ING_QUIMICA', 'Ingeniería Química'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('LIC_BIOTECNOLOGIA', 'Licenciatura en Biotecnología'),
            ],
            'UACB': [
                ('ING_CIVIL', 'Ingeniería Civil'),
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('ING_INDUSTRIAL', 'Ingeniería Industrial'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('TEC_ELECTRONICA', 'Técnico Superior en Electrónica'),
                ('TEC_SISTEMAS', 'Técnico Superior en Sistemas'),
            ],
            'UATP': [
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('TEC_CONSTRUCCIONES', 'Técnico Superior en Construcciones Civiles'),
                ('TEC_TOPOGRAFIA', 'Técnico Superior en Topografía'),
            ],
            'UCRB': [
                ('ING_COMERCIAL', 'Ingeniería Comercial'),
                ('ING_SISTEMAS', 'Ingeniería de Sistemas'),
                ('TEC_MECANICA', 'Técnico Superior en Mecánica Industrial'),
                ('TEC_ELECTROMECANICA', 'Técnico Superior en Electromecánica'),
            ]
        }
        
        total_creadas = 0
        
        print("\n📚 Creando carreras por unidad académica:")
        for unidad_nombre, carreras in carreras_por_unidad.items():
            try:
                unidad = UnidadAcademica.objects.get(nombre=unidad_nombre)
                print(f"\n  🏛️  {unidad_nombre} ({unidad.get_nombre_display()}):")
                
                for carrera_codigo, carrera_nombre in carreras:
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
                        
            except UnidadAcademica.DoesNotExist:
                print(f"    ❌ Unidad {unidad_nombre} no encontrada")
        
        print(f"\n🎯 Total de carreras creadas: {total_creadas}")

def verificar_carreras_por_unidad():
    """Verifica que cada unidad académica tenga carreras asignadas"""
    print("\n🔍 VERIFICACIÓN DE CARRERAS POR UNIDAD:")
    print("=" * 45)
    
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
                print(f"   • {carrera.get_nombre_display()}")
        else:
            print("   ⚠️  Sin carreras asignadas")
    
    print(f"\n📊 RESUMEN TOTAL: {total_carreras} carreras en {unidades.count()} unidades")

def probar_api_carreras():
    """Prueba la funcionalidad de la API de carreras"""
    print("\n🔗 PRUEBA DE API DE CARRERAS:")
    print("=" * 35)
    
    mapeo_unidades = {
        'la_paz': 'UALP',
        'santa_cruz': 'UASC', 
        'cochabamba': 'UACB',
        'riberalta': 'UCRB',
        'tropico': 'UATP'
    }
    
    for key, unidad_nombre in mapeo_unidades.items():
        try:
            unidad = UnidadAcademica.objects.get(nombre=unidad_nombre)
            carreras = Carrera.objects.filter(unidad_academica=unidad)
            
            print(f"\n📍 '{key}' → {unidad_nombre}:")
            print(f"   🎓 Carreras disponibles: {carreras.count()}")
            
            for carrera in carreras[:3]:  # Mostrar solo las primeras 3
                print(f"   • {carrera.get_nombre_display()}")
            
            if carreras.count() > 3:
                print(f"   ... y {carreras.count() - 3} más")
                
        except UnidadAcademica.DoesNotExist:
            print(f"❌ '{key}' → {unidad_nombre}: UNIDAD NO ENCONTRADA")

if __name__ == "__main__":
    print("🎓 CORRECCIÓN DE CARRERAS CON UNIDADES ACADÉMICAS OFICIALES")
    print("=" * 65)
    
    # Limpiar y recrear carreras
    limpiar_y_crear_carreras()
    
    # Verificar resultado
    verificar_carreras_por_unidad()
    
    # Probar API
    probar_api_carreras()
    
    print("\n✅ CORRECCIÓN COMPLETADA")
    print("💡 Las carreras ahora están correctamente asociadas a las unidades académicas oficiales")
    print("🚀 Las APIs de carreras deberían funcionar correctamente")
