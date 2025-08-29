#!/usr/bin/env python3
"""
Script para limpiar y sincronizar las carreras en la base de datos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, UnidadAcademica
from django.db import transaction

def limpiar_y_actualizar_carreras():
    """Limpiar duplicados y actualizar carreras según la lista oficial"""
    
    print("🔄 LIMPIANDO Y ACTUALIZANDO CARRERAS OFICIALES")
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
    
    with transaction.atomic():
        # 1. Identificar y manejar duplicados
        print("🔍 Identificando duplicados...")
        duplicados_encontrados = {}
        
        for codigo, nombre_legible in carreras_oficiales:
            carreras_mismo_codigo = Carrera.objects.filter(nombre=codigo)
            if carreras_mismo_codigo.count() > 1:
                duplicados_encontrados[codigo] = list(carreras_mismo_codigo)
                print(f"⚠️  Duplicados encontrados para {nombre_legible}: {carreras_mismo_codigo.count()}")
        
        # 2. Resolver duplicados (mantener el primero, eliminar los demás)
        if duplicados_encontrados:
            print("🧹 Resolviendo duplicados...")
            for codigo, carreras_duplicadas in duplicados_encontrados.items():
                # Mantener la primera, eliminar las demás
                carrera_principal = carreras_duplicadas[0]
                carreras_a_eliminar = carreras_duplicadas[1:]
                
                print(f"  📌 Manteniendo carrera ID {carrera_principal.id} para {codigo}")
                for carrera_dup in carreras_a_eliminar:
                    print(f"  🗑️  Eliminando duplicado ID {carrera_dup.id}")
                    carrera_dup.delete()
        
        # 3. Obtener unidad académica de referencia
        try:
            unidad_referencia = UnidadAcademica.objects.get(nombre='UACB')
        except UnidadAcademica.DoesNotExist:
            unidad_referencia = UnidadAcademica.objects.first()
            if not unidad_referencia:
                print("❌ Error: No hay unidades académicas en la BD")
                return
        
        print(f"\n🏛️ Usando unidad de referencia: {unidad_referencia.nombre}")
        
        # 4. Crear carreras faltantes
        print("\n📝 Creando carreras faltantes...")
        carreras_creadas = 0
        carreras_existentes = 0
        
        for codigo, nombre_legible in carreras_oficiales:
            try:
                carrera = Carrera.objects.get(nombre=codigo)
                carreras_existentes += 1
                print(f"✅ Existente: {nombre_legible}")
            except Carrera.DoesNotExist:
                carrera = Carrera.objects.create(
                    nombre=codigo,
                    unidad_academica=unidad_referencia,
                    descripcion=f'Carrera de {nombre_legible}'
                )
                carreras_creadas += 1
                print(f"🆕 Creada: {nombre_legible}")
        
        # 5. Identificar carreras no oficiales
        codigos_oficiales = [codigo for codigo, _ in carreras_oficiales]
        carreras_no_oficiales = Carrera.objects.exclude(nombre__in=codigos_oficiales)
        
        print(f"\n📊 RESUMEN:")
        print(f"✅ Carreras existentes: {carreras_existentes}")
        print(f"🆕 Carreras creadas: {carreras_creadas}")
        print(f"📋 Total carreras oficiales: {len(carreras_oficiales)}")
        
        if carreras_no_oficiales.exists():
            print(f"\n⚠️  CARRERAS NO OFICIALES ENCONTRADAS ({carreras_no_oficiales.count()}):")
            for carrera in carreras_no_oficiales:
                print(f"  - {carrera.nombre}")
            
            print("\n¿Qué desea hacer con las carreras no oficiales?")
            print("1. Eliminar (recomendado)")
            print("2. Conservar")
            opcion = input("Seleccione opción (1/2): ").strip()
            
            if opcion == "1":
                eliminadas = carreras_no_oficiales.count()
                carreras_no_oficiales.delete()
                print(f"🗑️  Eliminadas {eliminadas} carreras no oficiales")
            else:
                print("⏭️  Carreras no oficiales conservadas")
        
        print(f"\n🎉 ¡Actualización completada!")
        print(f"\n📋 CARRERAS FINALES EN SISTEMA ({Carrera.objects.count()}):")
        
        for carrera in Carrera.objects.all().order_by('nombre'):
            # Obtener el nombre legible desde las opciones del modelo
            nombre_legible = dict(carreras_oficiales).get(carrera.nombre, carrera.nombre)
            print(f"  ✓ {nombre_legible}")

if __name__ == "__main__":
    limpiar_y_actualizar_carreras()
