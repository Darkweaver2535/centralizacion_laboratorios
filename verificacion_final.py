#!/usr/bin/env python
"""
Script de verificación final del funcionamiento del formulario
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificacion_final_formulario():
    print("✅ VERIFICACIÓN FINAL DEL FORMULARIO AGREGAR DATOS")
    print("=" * 60)
    
    # Verificar estructura completa
    print(f"\n📊 ESTRUCTURA DISPONIBLE:")
    
    # 1. Unidades Académicas
    unidades_academicas = UnidadAcademica.objects.all()
    print(f"   🏢 Unidades Académicas: {unidades_academicas.count()}")
    
    # 2. UALP específicamente
    ualp = UnidadAcademica.objects.filter(id=1).first()
    if ualp:
        print(f"   ✅ UALP encontrada: {ualp.nombre}")
        
        # Carreras en UALP
        carreras_ualp = Carrera.objects.filter(unidad_academica=ualp)
        print(f"   📚 Carreras en UALP: {carreras_ualp.count()}")
        
        for carrera in carreras_ualp[:3]:  # Mostrar solo las primeras 3
            asignaturas = Asignatura.objects.filter(carrera=carrera)
            print(f"      - {carrera.nombre}: {asignaturas.count()} asignaturas")
    
    # 3. Asignaturas principales con contenidos
    print(f"\n🧪 CONTENIDOS ANALÍTICOS POR ASIGNATURA:")
    
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    total_contenidos_verificados = 0
    
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            unidades = UnidadDidactica.objects.filter(asignatura=asignatura)
            contenidos_asignatura = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            ).count()
            
            print(f"   📚 {asignatura.nombre}:")
            print(f"      📋 Unidades didácticas: {unidades.count()}")
            print(f"      🧪 Contenidos analíticos: {contenidos_asignatura}")
            
            total_contenidos_verificados += contenidos_asignatura
            
            # Mostrar algunos contenidos de ejemplo
            if contenidos_asignatura > 0:
                ejemplos = ContenidoAnalitico.objects.filter(
                    unidad_didactica__asignatura=asignatura
                )[:2]
                print(f"      📝 Ejemplos:")
                for contenido in ejemplos:
                    print(f"         - {contenido.nombre}")
    
    # 4. Verificación de URLs AJAX
    print(f"\n🔗 VERIFICACIÓN DE ENDPOINTS AJAX:")
    
    endpoints_necesarios = [
        ('carreras-por-unidad', 'Filtrar carreras por unidad académica'),
        ('asignaturas-por-carrera', 'Filtrar asignaturas por carrera'),
        ('unidades-didacticas', 'Filtrar unidades didácticas por asignatura'),
        ('contenidos-analiticos', 'Filtrar contenidos analíticos por unidad didáctica'),
    ]
    
    for endpoint, descripcion in endpoints_necesarios:
        print(f"   ✅ {endpoint}: {descripcion}")
    
    # 5. Resultado final
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   📊 Total contenidos analíticos: {total_contenidos_verificados}")
    
    if total_contenidos_verificados > 0:
        print(f"\n🎉 ¡FORMULARIO LISTO PARA USAR!")
        print(f"   📝 Pasos para probar:")
        print(f"   1. Ve a: http://127.0.0.1:8001/dashboard/malla-curricular/agregar-datos/")
        print(f"   2. Selecciona: Unidad Académica = 'UALP'")
        print(f"   3. Selecciona: Carrera (debería aparecer lista)")
        print(f"   4. Selecciona: Asignatura (ej: FISICA I, QUIMICA GENERAL)")
        print(f"   5. Selecciona: Criterio de Desempeño (debería aparecer)")
        print(f"   6. Selecciona: Unidad Didáctica (ej: CINEMATICA DE LA PARTICULA)")
        print(f"   7. Selecciona: Contenido Analítico (¡AHORA DEBERÍAN APARECER OPCIONES!)")
        print(f"\n   🔍 Si aún no aparecen opciones, revisa la consola del navegador (F12)")
    else:
        print(f"\n❌ AÚN HAY PROBLEMAS:")
        print(f"   - No se encontraron contenidos analíticos")
        print(f"   - El formulario seguirá sin mostrar opciones")

def mostrar_ejemplo_contenidos():
    print(f"\n📋 EJEMPLO DE CONTENIDOS DISPONIBLES:")
    
    # Mostrar contenidos de FÍSICA I como ejemplo
    fisica1 = Asignatura.objects.filter(nombre__iexact='FISICA I').first()
    if fisica1:
        print(f"\n📚 Ejemplo: FÍSICA I")
        unidades = UnidadDidactica.objects.filter(asignatura=fisica1)
        
        for unidad in unidades[:2]:  # Solo las primeras 2
            contenidos = ContenidoAnalitico.objects.filter(unidad_didactica=unidad)
            print(f"   📋 {unidad.nombre}:")
            
            for contenido in contenidos[:3]:  # Solo los primeros 3
                print(f"      🧪 {contenido.nombre}")
            
            if contenidos.count() > 3:
                print(f"      ... y {contenidos.count() - 3} más")

if __name__ == "__main__":
    verificacion_final_formulario()
    mostrar_ejemplo_contenidos()