#!/usr/bin/env python
"""
Script final para limpiar todos los restos de nuestras pruebas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def limpiar_restos_pruebas():
    print("🧹 LIMPIEZA FINAL DE RESTOS DE PRUEBAS")
    print("=" * 60)
    
    eliminados = 0
    
    # Buscar y limpiar títulos con nuestras palabras de prueba
    palabras_prueba = ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA']
    
    print("\n📝 Limpiando títulos de prueba...")
    for palabra in palabras_prueba:
        titulos = Titulo.objects.filter(texto__icontains=palabra)
        count = titulos.count()
        if count > 0:
            print(f"   🗑️ Eliminando {count} títulos con '{palabra}'")
            for titulo in titulos:
                print(f"      - '{titulo.texto}' del contenido: {titulo.contenido_analitico.nombre}")
            titulos.delete()
            eliminados += count
    
    # Buscar y limpiar bibliografías con datos de prueba
    print("\n📚 Limpiando bibliografías de prueba...")
    bibliografias_prueba = Bibliografia.objects.filter(
        titulo__in=['nnnknk', 'vvvvvvvvv', 'labubu', 'nnnnn', 'vcvcmdvxm,cn']
    )
    count_biblio = bibliografias_prueba.count()
    if count_biblio > 0:
        print(f"   🗑️ Eliminando {count_biblio} bibliografías de prueba")
        bibliografias_prueba.delete()
    
    # Buscar y limpiar prácticas de laboratorio con datos de prueba
    print("\n🔬 Limpiando prácticas de laboratorio de prueba...")
    practicas_prueba = PracticaLaboratorio.objects.filter(
        nombre__in=['hhhhhhh', 'nknjnnj', 'iojjijiji', 'mmvv,vn,m']
    )
    count_practicas = practicas_prueba.count()
    if count_practicas > 0:
        print(f"   🗑️ Eliminando {count_practicas} prácticas de laboratorio de prueba")
        practicas_prueba.delete()
    
    # Buscar contenidos analíticos que contengan solo nuestros datos de prueba
    print("\n🧪 Verificando contenidos analíticos...")
    contenidos = ContenidoAnalitico.objects.all()
    
    for contenido in contenidos:
        # Verificar si este contenido tiene solo datos de prueba nuestros
        titulos = Titulo.objects.filter(contenido_analitico=contenido)
        tiene_solo_pruebas = False
        
        for titulo in titulos:
            if any(palabra in titulo.texto for palabra in ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA']):
                tiene_solo_pruebas = True
                
        if tiene_solo_pruebas and not any(palabra not in titulo.texto for titulo in titulos for palabra in ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA']):
            # Este contenido solo tiene datos de prueba, eliminarlo completamente
            asignatura = contenido.unidad_didactica.asignatura
            print(f"   🗑️ Eliminando contenido completo: '{contenido.nombre}' en {asignatura.nombre}")
            contenido.delete()
            eliminados += 1
    
    print(f"\n🎉 LIMPIEZA COMPLETADA")
    print(f"   📊 Total elementos eliminados: {eliminados}")
    print(f"   ✨ Base de datos preparada para pruebas profesionales")

def verificar_estado_final():
    print(f"\n🔍 VERIFICACIÓN FINAL DEL ESTADO")
    print("=" * 40)
    
    # Verificar que no queden rastros de pruebas
    palabras_buscar = ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA']
    
    rastros_encontrados = 0
    
    for palabra in palabras_buscar:
        # Títulos
        titulos = Titulo.objects.filter(texto__icontains=palabra)
        if titulos.exists():
            print(f"   ⚠️ Quedan {titulos.count()} títulos con '{palabra}'")
            rastros_encontrados += titulos.count()
        
        # Contenidos analíticos
        contenidos = ContenidoAnalitico.objects.filter(nombre__icontains=palabra)
        if contenidos.exists():
            print(f"   ⚠️ Quedan {contenidos.count()} contenidos con '{palabra}'")
            rastros_encontrados += contenidos.count()
    
    if rastros_encontrados == 0:
        print("   ✅ Perfecto - No quedan rastros de pruebas")
        print("   🎯 Listo para pruebas profesionales")
    else:
        print(f"   ⚠️ Aún quedan {rastros_encontrados} elementos de prueba")

if __name__ == "__main__":
    limpiar_restos_pruebas()
    verificar_estado_final()