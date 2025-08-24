#!/usr/bin/env python
"""
Script para distribuir las carreras a todas las unidades académicas
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, UnidadAcademica
from django.db import transaction

def distribuir_carreras_todas_unidades():
    """Crear las carreras para todas las unidades académicas"""
    print("🎓 Distribuyendo carreras a todas las unidades académicas...")
    
    # Lista de carreras requeridas
    carreras_licenciatura = [
        "Ingeniería Civil",
        "Ingeniería Geográfica", 
        "Ingeniería en Sistemas Electrónicos",
        "Ingeniería Industrial",
        "Ingeniería Comercial",
        "Ingeniería de Sistemas",
        "Ingeniería Ambiental",
        "Ingeniería Petrolera",
        "Ingeniería Mecatrónica",
        "Ingeniería en Telecomunicaciones",
        "Ingeniería Financiera",
        "Ingeniería Agroindustrial",
        "Ingeniería Agronómica"
    ]
    
    carreras_tecnicas = [
        "Informática",
        "Sistemas Electrónicos", 
        "Energías Renovables",
        "Construcción Civil",
        "Diseño Gráfico y Comunicación Audiovisual"
    ]
    
    todas_las_carreras = carreras_licenciatura + carreras_tecnicas
    
    try:
        with transaction.atomic():
            # Obtener todas las unidades académicas
            unidades = UnidadAcademica.objects.all()
            print(f"📍 Unidades académicas encontradas: {unidades.count()}")
            
            for unidad in unidades:
                print(f"\n🏛️  Procesando unidad: {unidad.nombre}")
                
                # Crear carreras de licenciatura para esta unidad
                for nombre_carrera in carreras_licenciatura:
                    carrera, created = Carrera.objects.get_or_create(
                        nombre=nombre_carrera,
                        unidad_academica=unidad,
                        defaults={
                            'descripcion': f'Carrera de {nombre_carrera}'
                        }
                    )
                    if created:
                        print(f"   ✅ Creada: {nombre_carrera}")
                    else:
                        print(f"   ℹ️  Ya existe: {nombre_carrera}")
                
                # Crear carreras técnicas para esta unidad
                for nombre_carrera in carreras_tecnicas:
                    carrera, created = Carrera.objects.get_or_create(
                        nombre=nombre_carrera,
                        unidad_academica=unidad,
                        defaults={
                            'descripcion': f'Carrera técnica de {nombre_carrera}'
                        }
                    )
                    if created:
                        print(f"   ✅ Creada técnica: {nombre_carrera}")
                    else:
                        print(f"   ℹ️  Ya existe técnica: {nombre_carrera}")
            
            print(f"\n📊 Total de carreras en sistema: {Carrera.objects.count()}")
            return True
            
    except Exception as e:
        print(f"❌ Error al distribuir carreras: {str(e)}")
        return False

def verificar_distribucion():
    """Verificar que cada unidad tenga todas las carreras"""
    print("\n🔍 Verificando distribución de carreras...")
    
    unidades = UnidadAcademica.objects.all()
    carreras_esperadas = 18  # 13 licenciaturas + 5 técnicas
    
    for unidad in unidades:
        carreras_count = Carrera.objects.filter(unidad_academica=unidad).count()
        print(f"📍 {unidad.nombre}: {carreras_count} carreras")
        
        if carreras_count != carreras_esperadas:
            print(f"   ⚠️  Esperadas: {carreras_esperadas}, Encontradas: {carreras_count}")
        else:
            print(f"   ✅ Completa ({carreras_esperadas} carreras)")
    
    print(f"\n📈 Resumen:")
    print(f"   - Total unidades: {unidades.count()}")
    print(f"   - Total carreras: {Carrera.objects.count()}")
    print(f"   - Esperado: {unidades.count() * carreras_esperadas}")

def main():
    print("🚀 DISTRIBUYENDO CARRERAS A TODAS LAS UNIDADES ACADÉMICAS")
    print("=" * 70)
    print("📌 Objetivo: Todas las carreras disponibles en todas las unidades")
    print("=" * 70)
    
    # Distribuir carreras
    if distribuir_carreras_todas_unidades():
        print("✅ Carreras distribuidas correctamente")
    else:
        print("❌ Error distribuyendo carreras")
        return False
    
    # Verificar distribución
    verificar_distribucion()
    
    print("\n🎉 ¡Distribución completada!")
    print("🔧 Ahora todas las unidades académicas tienen todas las carreras disponibles")
    
    return True

if __name__ == "__main__":
    main()
