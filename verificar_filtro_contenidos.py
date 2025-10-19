#!/usr/bin/env python
"""
Script para verificar que solo se muestran contenidos con datos reales
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_filtro_contenidos():
    print("🔍 VERIFICANDO FILTRO DE CONTENIDOS CON DATOS REALES")
    print("=" * 60)
    
    # Verificar asignaturas principales
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            print(f"\n📚 {asignatura.nombre} (ID: {asignatura.id}):")
            
            # Todos los contenidos analíticos
            todos_contenidos = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            )
            
            # Contenidos CON datos (como los filtra la vista ahora)
            contenidos_con_datos = []
            contenidos_vacios = []
            
            for contenido in todos_contenidos:
                tiene_datos = (
                    Competencias.objects.filter(contenido_analitico=contenido).exists() or
                    ObjetivoPractica.objects.filter(contenido_analitico=contenido).exists() or
                    Procedimientos.objects.filter(contenido_analitico=contenido).exists() or
                    MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).exists() or
                    FundamentoTeorico.objects.filter(contenido_analitico=contenido).exists() or
                    CalculosResultados.objects.filter(contenido_analitico=contenido).exists() or
                    Cuestionario.objects.filter(contenido_analitico=contenido).exists() or
                    Bibliografia.objects.filter(contenido_analitico=contenido).exists() or
                    Titulo.objects.filter(contenido_analitico=contenido).exists()
                )
                
                if tiene_datos:
                    contenidos_con_datos.append(contenido)
                else:
                    contenidos_vacios.append(contenido)
            
            print(f"   📊 Total contenidos: {todos_contenidos.count()}")
            print(f"   ✅ Con datos reales: {len(contenidos_con_datos)} (SE MOSTRARÁN)")
            print(f"   🙈 Vacíos/esqueletos: {len(contenidos_vacios)} (SE OCULTARÁN)")
            
            # Mostrar algunos ejemplos de contenidos vacíos que se ocultarán
            if contenidos_vacios:
                print(f"   🔕 Ejemplos de contenidos OCULTOS:")
                for contenido in contenidos_vacios[:3]:
                    print(f"      - {contenido.nombre}")
                if len(contenidos_vacios) > 3:
                    print(f"      ... y {len(contenidos_vacios) - 3} más")
            
            # Mostrar contenidos que SÍ aparecerán
            if contenidos_con_datos:
                print(f"   👁️ Ejemplos de contenidos VISIBLES:")
                for contenido in contenidos_con_datos[:3]:
                    print(f"      - {contenido.nombre}")
                if len(contenidos_con_datos) > 3:
                    print(f"      ... y {len(contenidos_con_datos) - 3} más")
    
    # Verificación específica para FISICOQUIMICA (la que mencionó el usuario)
    print(f"\n🎯 VERIFICACIÓN ESPECÍFICA - FISICOQUIMICA:")
    
    fisicoquimica = Asignatura.objects.filter(nombre__iexact='FISICOQUIMICA').first()
    if fisicoquimica:
        contenidos_fisico = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=fisicoquimica
        )
        
        contenidos_que_aparecian_antes = [
            'Factor de Compresibilidad',
            'Principio de Estados Correspondientes', 
            'Estados Críticos',
            'Ecuación de Van der Waals',
            'Humedad Relativa',
            'Ley de Graham',
            'Ley de Dalton',
            'Ecuación de Estado de Gases Ideales'
        ]
        
        print(f"   📋 Contenidos que aparecían antes y ahora se OCULTAN:")
        
        for nombre in contenidos_que_aparecian_antes:
            contenido = contenidos_fisico.filter(nombre__iexact=nombre).first()
            if contenido:
                tiene_datos = (
                    Competencias.objects.filter(contenido_analitico=contenido).exists() or
                    ObjetivoPractica.objects.filter(contenido_analitico=contenido).exists() or
                    Procedimientos.objects.filter(contenido_analitico=contenido).exists() or
                    MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).exists()
                )
                
                if tiene_datos:
                    print(f"      ✅ '{nombre}' - SE MOSTRARÁ (tiene datos)")
                else:
                    print(f"      🙈 '{nombre}' - SE OCULTARÁ (vacío)")
    
    print(f"\n🎉 RESULTADO ESPERADO:")
    print(f"   🙈 Los contenidos vacíos (Factor de Compresibilidad, etc.) ya NO aparecerán")
    print(f"   👁️ Solo aparecerán las prácticas que el usuario cree con datos reales")
    print(f"   ✨ La página se verá limpia y profesional")

if __name__ == "__main__":
    verificar_filtro_contenidos()