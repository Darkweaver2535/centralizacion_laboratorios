#!/usr/bin/env python
"""
Reporte final del estado de la base de datos después de la limpieza
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def reporte_estado_final():
    print("📊 REPORTE FINAL - ESTADO DE LA BASE DE DATOS")
    print("=" * 60)
    
    # Asignaturas principales
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            contenidos = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            ).count()
            
            print(f"\n📚 {asignatura.nombre} (ID: {asignatura.id})")
            print(f"   🧪 Contenidos analíticos: {contenidos}")
            
            # Mostrar algunos ejemplos de contenidos
            ejemplos = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            )[:3]
            
            for contenido in ejemplos:
                print(f"      - {contenido.nombre}")
    
    # Estadísticas generales
    print(f"\n📈 ESTADÍSTICAS GENERALES:")
    print(f"   🧪 Total contenidos analíticos: {ContenidoAnalitico.objects.count()}")
    print(f"   📝 Total títulos: {Titulo.objects.count()}")
    print(f"   📚 Total bibliografías: {Bibliografia.objects.count()}")
    print(f"   📋 Total auditorías: {AuditoriaCreacionPractica.objects.count()}")
    
    # Verificar que no queden pruebas
    palabras_prueba = ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA', 'TEST']
    rastros = 0
    
    for palabra in palabras_prueba:
        contenidos = ContenidoAnalitico.objects.filter(nombre__icontains=palabra)
        titulos = Titulo.objects.filter(texto__icontains=palabra)
        rastros += contenidos.count() + titulos.count()
    
    if rastros == 0:
        print(f"\n✅ ESTADO: LIMPIO - Listo para pruebas profesionales")
        print(f"   🎯 No se encontraron rastros de pruebas anteriores")
        print(f"   🚀 Sistema preparado para uso en producción")
    else:
        print(f"\n⚠️ ADVERTENCIA: Se encontraron {rastros} elementos que podrían ser pruebas")

if __name__ == "__main__":
    reporte_estado_final()