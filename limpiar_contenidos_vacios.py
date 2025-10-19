#!/usr/bin/env python
"""
Script para identificar y eliminar contenidos analíticos vacíos o incompletos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def identificar_contenidos_vacios():
    print("🔍 IDENTIFICANDO CONTENIDOS ANALÍTICOS VACÍOS")
    print("=" * 60)
    
    contenidos_vacios = []
    
    # Obtener todos los contenidos analíticos
    todos_contenidos = ContenidoAnalitico.objects.all()
    
    for contenido in todos_contenidos:
        # Verificar si el contenido está vacío (sin datos profesionales)
        competencias = Competencias.objects.filter(contenido_analitico=contenido).exists()
        objetivos = ObjetivoPractica.objects.filter(contenido_analitico=contenido).exists()
        procedimientos = Procedimientos.objects.filter(contenido_analitico=contenido).exists()
        fundamentos = FundamentoTeorico.objects.filter(contenido_analitico=contenido).exists()
        materiales = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).exists()
        titulos = Titulo.objects.filter(contenido_analitico=contenido).exists()
        bibliografias = Bibliografia.objects.filter(contenido_analitico=contenido).exists()
        practicas = PracticaLaboratorio.objects.filter(contenido_analitico=contenido).exists()
        calculos = CalculosResultados.objects.filter(contenido_analitico=contenido).exists()
        cuestionarios = Cuestionario.objects.filter(contenido_analitico=contenido).exists()
        
        # Si no tiene NINGÚN dato asociado, está vacío
        esta_vacio = not any([
            competencias, objetivos, procedimientos, fundamentos, 
            materiales, titulos, bibliografias, practicas, calculos, cuestionarios
        ])
        
        if esta_vacio:
            asignatura = contenido.unidad_didactica.asignatura
            unidad = contenido.unidad_didactica
            
            contenidos_vacios.append({
                'contenido': contenido,
                'asignatura': asignatura.nombre,
                'unidad': unidad.nombre,
                'nombre': contenido.nombre
            })
    
    # Mostrar contenidos vacíos por asignatura
    asignaturas_con_vacios = {}
    for item in contenidos_vacios:
        asignatura = item['asignatura']
        if asignatura not in asignaturas_con_vacios:
            asignaturas_con_vacios[asignatura] = []
        asignaturas_con_vacios[asignatura].append(item)
    
    total_vacios = len(contenidos_vacios)
    
    for asignatura, items in asignaturas_con_vacios.items():
        print(f"\n📚 {asignatura} - {len(items)} contenidos vacíos:")
        for item in items[:10]:  # Mostrar solo los primeros 10
            print(f"   🗑️ '{item['nombre']}' en unidad: {item['unidad']}")
        if len(items) > 10:
            print(f"   ... y {len(items) - 10} más")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Total contenidos analizados: {todos_contenidos.count()}")
    print(f"   Total contenidos vacíos encontrados: {total_vacios}")
    print(f"   Porcentaje vacío: {(total_vacios/todos_contenidos.count()*100):.1f}%")
    
    return contenidos_vacios

def eliminar_contenidos_vacios(contenidos_vacios):
    print(f"\n🗑️ ELIMINANDO {len(contenidos_vacios)} CONTENIDOS VACÍOS")
    print("=" * 50)
    
    eliminados_por_asignatura = {}
    
    for item in contenidos_vacios:
        contenido = item['contenido']
        asignatura = item['asignatura']
        
        if asignatura not in eliminados_por_asignatura:
            eliminados_por_asignatura[asignatura] = 0
        
        print(f"   🗑️ Eliminando: '{contenido.nombre}' de {asignatura}")
        contenido.delete()
        eliminados_por_asignatura[asignatura] += 1
    
    print(f"\n✅ ELIMINACIÓN COMPLETADA:")
    for asignatura, count in eliminados_por_asignatura.items():
        print(f"   📚 {asignatura}: {count} contenidos eliminados")
    
    print(f"\n🎉 Total eliminados: {len(contenidos_vacios)}")

def verificar_estado_post_limpieza():
    print(f"\n🔍 VERIFICACIÓN POST-LIMPIEZA")
    print("=" * 40)
    
    # Verificar contenidos restantes por asignatura
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    total_restantes = 0
    
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            contenidos_count = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            ).count()
            
            # Verificar cuántos tienen datos reales
            contenidos_con_datos = 0
            contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asignatura)
            
            for contenido in contenidos:
                tiene_datos = any([
                    Competencias.objects.filter(contenido_analitico=contenido).exists(),
                    ObjetivoPractica.objects.filter(contenido_analitico=contenido).exists(),
                    Procedimientos.objects.filter(contenido_analitico=contenido).exists(),
                    FundamentoTeorico.objects.filter(contenido_analitico=contenido).exists(),
                    MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).exists(),
                ])
                
                if tiene_datos:
                    contenidos_con_datos += 1
            
            print(f"   📚 {asignatura.nombre}:")
            print(f"      🧪 Total contenidos: {contenidos_count}")
            print(f"      ✅ Con datos reales: {contenidos_con_datos}")
            print(f"      🗑️ Vacíos restantes: {contenidos_count - contenidos_con_datos}")
            
            total_restantes += contenidos_count
    
    print(f"\n📈 RESUMEN FINAL:")
    print(f"   🧪 Total contenidos restantes: {total_restantes}")
    print(f"   ✨ Base de datos optimizada para uso profesional")

if __name__ == "__main__":
    contenidos_vacios = identificar_contenidos_vacios()
    
    if contenidos_vacios:
        respuesta = input(f"\n¿Eliminar {len(contenidos_vacios)} contenidos vacíos? (s/n): ")
        if respuesta.lower() == 's':
            eliminar_contenidos_vacios(contenidos_vacios)
            verificar_estado_post_limpieza()
        else:
            print("❌ Eliminación cancelada")
    else:
        print("✅ No se encontraron contenidos vacíos")
        verificar_estado_post_limpieza()