#!/usr/bin/env python
"""
Script para limpiar todas las pruebas realizadas en las 4 asignaturas principales
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def limpiar_pruebas_testing():
    print("🧹 LIMPIANDO PRUEBAS DE TESTING")
    print("=" * 60)
    
    # Lista de palabras clave que identifican nuestras pruebas
    palabras_prueba = [
        'PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA', 'TEST', 'DEMO',
        'prueba', 'test', 'demo', 'ejemplo', 'temporal'
    ]
    
    # Asignaturas principales donde hicimos pruebas
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    total_eliminados = 0
    
    for nombre_asignatura in asignaturas_principales:
        print(f"\n📚 Limpiando {nombre_asignatura}...")
        
        try:
            asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asignatura).first()
            if not asignatura:
                print(f"   ⚠️ No se encontró la asignatura {nombre_asignatura}")
                continue
                
            print(f"   🎯 Procesando asignatura ID: {asignatura.id}")
            
            # Buscar contenidos analíticos con palabras de prueba
            contenidos_prueba = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            )
            
            eliminados_asignatura = 0
            
            for contenido in contenidos_prueba:
                es_prueba = False
                
                # Verificar si el nombre del contenido contiene palabras de prueba
                for palabra in palabras_prueba:
                    if palabra.lower() in contenido.nombre.lower():
                        es_prueba = True
                        break
                
                # Verificar títulos relacionados
                if not es_prueba:
                    titulos = Titulo.objects.filter(contenido_analitico=contenido)
                    for titulo in titulos:
                        for palabra in palabras_prueba:
                            if palabra.lower() in titulo.texto.lower():
                                es_prueba = True
                                break
                        if es_prueba:
                            break
                
                # Verificar bibliografías relacionadas
                if not es_prueba:
                    bibliografias = Bibliografia.objects.filter(contenido_analitico=contenido)
                    for biblio in bibliografias:
                        for palabra in palabras_prueba:
                            if palabra.lower() in biblio.titulo.lower():
                                es_prueba = True
                                break
                        if es_prueba:
                            break
                
                if es_prueba:
                    print(f"   🗑️ Eliminando: {contenido.nombre} (ID: {contenido.id})")
                    
                    # Eliminar todos los datos relacionados
                    Titulo.objects.filter(contenido_analitico=contenido).delete()
                    Bibliografia.objects.filter(contenido_analitico=contenido).delete()
                    PracticaLaboratorio.objects.filter(contenido_analitico=contenido).delete()
                    Competencias.objects.filter(contenido_analitico=contenido).delete()
                    ObjetivoPractica.objects.filter(contenido_analitico=contenido).delete()
                    FundamentoTeorico.objects.filter(contenido_analitico=contenido).delete()
                    MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).delete()
                    Procedimientos.objects.filter(contenido_analitico=contenido).delete()
                    CalculosResultados.objects.filter(contenido_analitico=contenido).delete()
                    Cuestionario.objects.filter(contenido_analitico=contenido).delete()
                    
                    # Eliminar el contenido analítico
                    contenido.delete()
                    
                    eliminados_asignatura += 1
                    total_eliminados += 1
            
            print(f"   ✅ Eliminados {eliminados_asignatura} contenidos de prueba")
            
        except Exception as e:
            print(f"   ❌ Error procesando {nombre_asignatura}: {e}")
    
    # Limpiar auditorías de pruebas
    print(f"\n🗂️ Limpiando auditorías de pruebas...")
    auditorias_prueba = AuditoriaCreacionPractica.objects.filter(
        practica_nombre__iregex=r'(prueba|labubu|final|funciona|test|demo)'
    )
    
    auditorias_eliminadas = auditorias_prueba.count()
    auditorias_prueba.delete()
    
    print(f"   ✅ Eliminadas {auditorias_eliminadas} auditorías de prueba")
    
    print(f"\n🎉 LIMPIEZA COMPLETADA:")
    print(f"   📊 Total contenidos eliminados: {total_eliminados}")
    print(f"   📋 Total auditorías eliminadas: {auditorias_eliminadas}")
    print(f"   ✨ Base de datos lista para pruebas profesionales")

def verificar_limpieza():
    print(f"\n🔍 VERIFICANDO LIMPIEZA...")
    print("=" * 40)
    
    palabras_prueba = [
        'PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA', 'TEST', 'DEMO'
    ]
    
    # Verificar contenidos restantes
    for palabra in palabras_prueba:
        contenidos = ContenidoAnalitico.objects.filter(nombre__icontains=palabra)
        if contenidos.exists():
            print(f"   ⚠️ Aún quedan contenidos con '{palabra}': {contenidos.count()}")
            for contenido in contenidos[:3]:  # Mostrar solo los primeros 3
                asignatura = contenido.unidad_didactica.asignatura
                print(f"      - {contenido.nombre} en {asignatura.nombre}")
        
        # Verificar títulos restantes
        titulos = Titulo.objects.filter(texto__icontains=palabra)
        if titulos.exists():
            print(f"   ⚠️ Aún quedan títulos con '{palabra}': {titulos.count()}")
    
    # Verificar auditorías restantes
    auditorias = AuditoriaCreacionPractica.objects.filter(
        practica_nombre__iregex=r'(prueba|labubu|final|funciona|test|demo)'
    )
    if auditorias.exists():
        print(f"   ⚠️ Aún quedan auditorías de prueba: {auditorias.count()}")
    
    if not any([
        ContenidoAnalitico.objects.filter(nombre__iregex=r'(prueba|labubu|final|funciona|test|demo)').exists(),
        Titulo.objects.filter(texto__iregex=r'(prueba|labubu|final|funciona|test|demo)').exists(),
        auditorias.exists()
    ]):
        print(f"   ✅ Limpieza completada exitosamente - No quedan pruebas")

if __name__ == "__main__":
    limpiar_pruebas_testing()
    verificar_limpieza()