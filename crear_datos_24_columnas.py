#!/usr/bin/env python3
"""
Script para poblar los nuevos campos de las 24 columnas oficiales
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    Asignatura, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico
)
from django.db import transaction

def crear_datos_24_columnas():
    """Crear datos básicos para los nuevos campos de las 24 columnas"""
    
    print("📊 CREANDO DATOS PARA LAS 24 COLUMNAS OFICIALES")
    print("=" * 50)
    
    with transaction.atomic():
        # Obtener asignaturas existentes
        asignaturas = Asignatura.objects.all()[:10]  # Primeras 10 asignaturas
        
        print(f"📋 Creando datos para {asignaturas.count()} asignaturas...")
        
        criterios_creados = 0
        unidades_creadas = 0
        contenidos_creados = 0
        
        for asignatura in asignaturas:
            # Crear criterios de desempeño básicos
            criterios_base = [
                f"Aplicar conceptos teóricos de {asignatura.nombre}",
                f"Desarrollar habilidades prácticas en {asignatura.nombre}",
                f"Evaluar resultados en experimentos de {asignatura.nombre}",
            ]
            
            for criterio_texto in criterios_base:
                criterio, created = CriterioDesempeno.objects.get_or_create(
                    nombre=criterio_texto[:200],  # Limitar a 200 caracteres
                    defaults={
                        'descripcion': f'Criterio de desempeño para la asignatura {asignatura.nombre}',
                        'asignatura': asignatura
                    }
                )
                if created:
                    criterios_creados += 1
                    print(f"   ✅ Criterio: {criterio.nombre[:50]}...")
            
            # Crear unidades didácticas básicas
            unidades_base = [
                f"Fundamentos de {asignatura.nombre}",
                f"Aplicaciones Prácticas de {asignatura.nombre}",
                f"Evaluación en {asignatura.nombre}",
            ]
            
            for unidad_texto in unidades_base:
                unidad, created = UnidadDidactica.objects.get_or_create(
                    nombre=unidad_texto[:200],  # Limitar a 200 caracteres
                    defaults={
                        'descripcion': f'Unidad didáctica para la asignatura {asignatura.nombre}',
                        'asignatura': asignatura
                    }
                )
                if created:
                    unidades_creadas += 1
                    print(f"   📚 Unidad: {unidad.nombre[:50]}...")
                
                # Crear contenidos analíticos para cada unidad didáctica
                contenidos_base = [
                    f"Conceptos básicos y definiciones de {unidad.nombre}",
                    f"Metodologías y procedimientos en {unidad.nombre}",
                    f"Ejercicios prácticos de {unidad.nombre}",
                ]
                
                for contenido_texto in contenidos_base:
                    contenido, created = ContenidoAnalitico.objects.get_or_create(
                        nombre=contenido_texto[:300],  # Limitar a 300 caracteres
                        defaults={
                            'descripcion': f'Contenido analítico detallado para {unidad.nombre}',
                            'unidad_didactica': unidad
                        }
                    )
                    if created:
                        contenidos_creados += 1
                        if contenidos_creados <= 5:  # Mostrar solo primeros 5
                            print(f"     📝 Contenido: {contenido.nombre[:40]}...")
        
        print(f"\n📊 RESUMEN DE CREACIÓN:")
        print(f"✅ Criterios de desempeño creados: {criterios_creados}")
        print(f"📚 Unidades didácticas creadas: {unidades_creadas}")
        print(f"📝 Contenidos analíticos creados: {contenidos_creados}")
        
        # Verificar totales
        print(f"\n📋 TOTALES EN SISTEMA:")
        print(f"   Criterios de desempeño: {CriterioDesempeno.objects.count()}")
        print(f"   Unidades didácticas: {UnidadDidactica.objects.count()}")
        print(f"   Contenidos analíticos: {ContenidoAnalitico.objects.count()}")
        
        print(f"\n✅ DATOS LISTOS PARA LAS 24 COLUMNAS OFICIALES")

if __name__ == "__main__":
    crear_datos_24_columnas()
