#!/usr/bin/env python
"""
Script para actualizar las Unidades Académicas y Carreras oficiales del EMI
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera

def actualizar_unidades_academicas():
    """Actualizar las unidades académicas oficiales"""
    unidades_oficiales = [
        'UALP',
        'UACB', 
        'UASC',
        'UATP',
        'UARB'
    ]
    
    print("=== ACTUALIZANDO UNIDADES ACADÉMICAS ===")
    
    # Primero, eliminar unidades que no están en la lista oficial
    unidades_existentes = UnidadAcademica.objects.all()
    for unidad in unidades_existentes:
        if unidad.nombre not in unidades_oficiales:
            print(f"❌ Eliminando unidad no oficial: {unidad.nombre}")
            unidad.delete()
    
    # Luego, crear las unidades oficiales que faltan
    for nombre_unidad in unidades_oficiales:
        unidad, created = UnidadAcademica.objects.get_or_create(
            nombre=nombre_unidad,
            defaults={'descripcion': f'Unidad Académica {nombre_unidad}'}
        )
        
        if created:
            print(f"✅ Creada unidad académica: {nombre_unidad}")
        else:
            print(f"✓ Unidad académica ya existe: {nombre_unidad}")
    
    print(f"\nTotal de unidades académicas: {UnidadAcademica.objects.count()}")

def actualizar_carreras():
    """Actualizar las carreras oficiales"""
    # Estas son las carreras oficiales según las choices del modelo
    carreras_oficiales = [
        'ING_CIVIL',
        'ING_GEOGRAFICA', 
        'ING_SISTEMAS_ELECTRONICOS',
        'ING_INDUSTRIAL',
        'ING_COMERCIAL',
        'ING_SISTEMAS',
        'ING_AMBIENTAL',
        'ING_PETROLERA',
        'ING_MECATRONICA',
        'ING_TELECOMUNICACIONES',
        'ING_FINANCIERA',
        'ING_AGROINDUSTRIAL',
        'ING_AGRONOMICA',
        'INFORMATICA',
        'SISTEMAS_ELECTRONICOS',
        'ENERGIAS_RENOVABLES',
        'CONSTRUCCION_CIVIL',
        'DISENO_GRAFICO'
    ]
    
    print("\n=== ACTUALIZANDO CARRERAS ===")
    
    # Primero, eliminar carreras que no están en la lista oficial
    carreras_existentes = Carrera.objects.all()
    for carrera in carreras_existentes:
        if carrera.nombre not in carreras_oficiales:
            print(f"❌ Eliminando carrera no oficial: {carrera.nombre}")
            carrera.delete()
    
    # Luego, crear las carreras oficiales que faltan
    # Usar UALP como unidad académica por defecto (se puede cambiar después)
    unidad_default = UnidadAcademica.objects.get(nombre='UALP')
    
    for codigo_carrera in carreras_oficiales:
        carrera, created = Carrera.objects.get_or_create(
            nombre=codigo_carrera,
            defaults={
                'unidad_academica': unidad_default,
                'descripcion': f'Carrera de {dict(Carrera.CARRERAS)[codigo_carrera]}'
            }
        )
        
        if created:
            print(f"✅ Creada carrera: {dict(Carrera.CARRERAS)[codigo_carrera]} ({codigo_carrera})")
        else:
            print(f"✓ Carrera ya existe: {dict(Carrera.CARRERAS)[codigo_carrera]} ({codigo_carrera})")
    
    print(f"\nTotal de carreras: {Carrera.objects.count()}")

def mostrar_resumen():
    """Mostrar resumen final"""
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    
    print("\n📋 UNIDADES ACADÉMICAS:")
    for ua in UnidadAcademica.objects.all().order_by('nombre'):
        print(f"  • {ua.nombre}")
    
    print(f"\n📋 CARRERAS ({Carrera.objects.count()} total):")
    for carrera in Carrera.objects.all().order_by('nombre'):
        print(f"  • {carrera.get_nombre_display()} ({carrera.nombre})")
    
    print("\n✅ Actualización completada exitosamente!")

if __name__ == '__main__':
    print("🚀 Iniciando actualización de Unidades Académicas y Carreras EMI")
    print("="*60)
    
    actualizar_unidades_academicas()
    actualizar_carreras()
    mostrar_resumen()
