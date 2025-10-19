#!/usr/bin/env python
"""
Script para verificar el estado de unidades didácticas y contenidos analíticos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_datos_formulario():
    print("🔍 VERIFICANDO DATOS PARA FORMULARIO AGREGAR DATOS")
    print("=" * 60)
    
    # Verificar asignaturas principales
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            print(f"\n📚 {asignatura.nombre} (ID: {asignatura.id}):")
            
            # Unidades didácticas
            unidades = UnidadDidactica.objects.filter(asignatura=asignatura)
            print(f"   📋 Unidades didácticas: {unidades.count()}")
            
            for unidad in unidades[:3]:  # Mostrar solo las primeras 3
                print(f"      - {unidad.nombre} (ID: {unidad.id})")
                
                # Contenidos analíticos por unidad
                contenidos = ContenidoAnalitico.objects.filter(unidad_didactica=unidad)
                print(f"        🧪 Contenidos: {contenidos.count()}")
            
            if unidades.count() > 3:
                print(f"      ... y {unidades.count() - 3} más")
    
    # Resumen total
    print(f"\n📊 RESUMEN TOTAL:")
    print(f"   📚 Total asignaturas: {Asignatura.objects.count()}")
    print(f"   📋 Total unidades didácticas: {UnidadDidactica.objects.count()}")
    print(f"   🧪 Total contenidos analíticos: {ContenidoAnalitico.objects.count()}")
    
    total_contenidos = ContenidoAnalitico.objects.count()
    if total_contenidos == 0:
        print(f"\n⚠️ PROBLEMA IDENTIFICADO:")
        print(f"   🔴 No hay contenidos analíticos en la base de datos")
        print(f"   🔴 Por eso el formulario no muestra opciones en 'Contenido Analítico'")
        print(f"   💡 SOLUCIÓN: Necesitamos crear algunos contenidos analíticos básicos")
    else:
        print(f"\n✅ Hay {total_contenidos} contenidos analíticos disponibles")

def crear_contenidos_basicos_demo():
    print(f"\n🛠️ CREANDO CONTENIDOS ANALÍTICOS BÁSICOS PARA DEMO")
    print("=" * 55)
    
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            unidades = UnidadDidactica.objects.filter(asignatura=asignatura)
            
            for unidad in unidades[:2]:  # Solo las primeras 2 unidades por asignatura
                # Crear un contenido analítico básico si no existe
                contenido_nombre = f"Contenido de {unidad.nombre}"
                
                contenido, created = ContenidoAnalitico.objects.get_or_create(
                    nombre=contenido_nombre,
                    unidad_didactica=unidad,
                    defaults={
                        'descripcion': f'Contenido analítico para {unidad.nombre} de {asignatura.nombre}'
                    }
                )
                
                if created:
                    print(f"   ✅ Creado: {contenido.nombre}")
                else:
                    print(f"   ℹ️ Ya existe: {contenido.nombre}")
    
    # Verificar resultado
    total_contenidos_nuevo = ContenidoAnalitico.objects.count()
    print(f"\n📈 RESULTADO:")
    print(f"   🧪 Total contenidos analíticos ahora: {total_contenidos_nuevo}")
    
    if total_contenidos_nuevo > 0:
        print(f"   🎉 ¡Formulario debería funcionar ahora!")
    else:
        print(f"   ⚠️ Aún hay problemas - verificar manualmente")

if __name__ == "__main__":
    verificar_datos_formulario()
    
    total_actual = ContenidoAnalitico.objects.count()
    if total_actual == 0:
        respuesta = input(f"\n¿Crear contenidos analíticos básicos para que funcione el formulario? (s/n): ")
        if respuesta.lower() == 's':
            crear_contenidos_basicos_demo()
        else:
            print("❌ No se crearon contenidos. El formulario seguirá sin opciones.")
    else:
        print(f"\n✅ Ya hay {total_actual} contenidos disponibles.")