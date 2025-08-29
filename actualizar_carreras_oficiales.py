#!/usr/bin/env python3
"""
Script para actualizar y sincronizar las carreras en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, UnidadAcademica

def actualizar_carreras():
    """Actualizar carreras según la lista oficial"""
    
    print("🔄 ACTUALIZANDO CARRERAS OFICIALES")
    print("=" * 50)
    
    # Lista oficial de carreras que deben existir
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
    
    # Verificar carreras existentes
    print("📋 Carreras actuales en BD:")
    carreras_existentes = Carrera.objects.all()
    for carrera in carreras_existentes.order_by('nombre'):
        print(f"  - {carrera.nombre}")
    
    print(f"\n📊 Total carreras en BD: {carreras_existentes.count()}")
    print(f"📊 Total carreras oficiales: {len(carreras_oficiales)}")
    
    # Obtener una unidad académica de referencia (UACB)
    try:
        unidad_referencia = UnidadAcademica.objects.get(nombre='UACB')
    except UnidadAcademica.DoesNotExist:
        # Si no existe, usar la primera disponible
        unidad_referencia = UnidadAcademica.objects.first()
        if not unidad_referencia:
            print("❌ Error: No hay unidades académicas en la BD")
            return
    
    print(f"\n🏛️ Usando unidad de referencia: {unidad_referencia.nombre}")
    
    # Crear o actualizar carreras
    carreras_creadas = 0
    carreras_actualizadas = 0
    
    for codigo, nombre in carreras_oficiales:
        carrera, created = Carrera.objects.get_or_create(
            nombre=codigo,
            defaults={
                'unidad_academica': unidad_referencia,
                'descripcion': f'Carrera de {nombre}'
            }
        )
        
        if created:
            carreras_creadas += 1
            print(f"✅ Creada: {nombre}")
        else:
            carreras_actualizadas += 1
            print(f"🔄 Existente: {nombre}")
    
    print(f"\n📊 RESUMEN:")
    print(f"✅ Carreras creadas: {carreras_creadas}")
    print(f"🔄 Carreras existentes: {carreras_actualizadas}")
    print(f"📋 Total final: {Carrera.objects.count()}")
    
    # Verificar si hay carreras extra que no están en la lista oficial
    codigos_oficiales = [codigo for codigo, _ in carreras_oficiales]
    carreras_extra = Carrera.objects.exclude(nombre__in=codigos_oficiales)
    
    if carreras_extra.exists():
        print(f"\n⚠️  CARRERAS NO OFICIALES ENCONTRADAS:")
        for carrera in carreras_extra:
            print(f"  - {carrera.nombre}")
        print(f"Total: {carreras_extra.count()}")
        
        respuesta = input("\n¿Desea eliminar las carreras no oficiales? (s/N): ").lower()
        if respuesta == 's':
            eliminadas = carreras_extra.count()
            carreras_extra.delete()
            print(f"✅ Eliminadas {eliminadas} carreras no oficiales")
        else:
            print("⏭️  Carreras no oficiales conservadas")
    
    print(f"\n🎉 ¡Actualización completada!")
    print(f"📋 Carreras finales en sistema:")
    for carrera in Carrera.objects.all().order_by('nombre'):
        # Obtener el nombre legible desde las opciones del modelo
        nombre_legible = dict(Carrera.CARRERAS).get(carrera.nombre, carrera.nombre)
        print(f"  - {nombre_legible}")

if __name__ == "__main__":
    actualizar_carreras()
