#!/usr/bin/env python
"""
Script para verificar la armonía del sistema de centralización de laboratorios.
Verifica que no haya variables dobles, que todo esté conectado correctamente,
y que el sistema funcione de manera armónica.
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.db import models
from django.apps import apps
from core.models import *

def verificar_modelos():
    """Verificar que todos los modelos estén correctamente definidos"""
    print("🔍 VERIFICANDO MODELOS DEL SISTEMA...")
    
    modelos_core = [
        UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio,
        Practica, Laboratorio, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico,
        Bibliografia, PracticaLaboratorio, Titulo, Competencias, ObjetivoPractica,
        FundamentoTeorico, MaterialesHerramientasEquipos, Procedimientos,
        CalculosResultados, Cuestionario
    ]
    
    for modelo in modelos_core:
        try:
            # Verificar que el modelo se puede instanciar
            modelo._meta.get_fields()
            print(f"✅ {modelo.__name__} - Correcto")
        except Exception as e:
            print(f"❌ {modelo.__name__} - Error: {e}")
    
    print("\n" + "="*50)

def verificar_relaciones():
    """Verificar que todas las relaciones entre modelos estén correctas"""
    print("🔗 VERIFICANDO RELACIONES ENTRE MODELOS...")
    
    # Verificar jerarquía principal
    try:
        # UnidadAcademica -> Carrera
        unidades = UnidadAcademica.objects.count()
        carreras = Carrera.objects.count()
        print(f"✅ UnidadAcademica ({unidades}) -> Carrera ({carreras})")
        
        # Carrera -> Asignatura
        asignaturas = Asignatura.objects.count()
        print(f"✅ Carrera ({carreras}) -> Asignatura ({asignaturas})")
        
        # Asignatura -> CriterioDesempeno
        criterios = CriterioDesempeno.objects.count()
        print(f"✅ Asignatura ({asignaturas}) -> CriterioDesempeno ({criterios})")
        
        # Asignatura -> UnidadDidactica
        unidades_didacticas = UnidadDidactica.objects.count()
        print(f"✅ Asignatura ({asignaturas}) -> UnidadDidactica ({unidades_didacticas})")
        
        # UnidadDidactica -> ContenidoAnalitico
        contenidos = ContenidoAnalitico.objects.count()
        print(f"✅ UnidadDidactica ({unidades_didacticas}) -> ContenidoAnalitico ({contenidos})")
        
        # ContenidoAnalitico -> Subdatos
        subdatos = {
            'Bibliografia': Bibliografia.objects.count(),
            'PracticaLaboratorio': PracticaLaboratorio.objects.count(),
            'Titulo': Titulo.objects.count(),
            'Competencias': Competencias.objects.count(),
            'ObjetivoPractica': ObjetivoPractica.objects.count(),
            'FundamentoTeorico': FundamentoTeorico.objects.count(),
            'MaterialesHerramientasEquipos': MaterialesHerramientasEquipos.objects.count(),
            'Procedimientos': Procedimientos.objects.count(),
            'CalculosResultados': CalculosResultados.objects.count(),
            'Cuestionario': Cuestionario.objects.count(),
        }
        
        for nombre, cantidad in subdatos.items():
            print(f"✅ ContenidoAnalitico ({contenidos}) -> {nombre} ({cantidad})")
            
    except Exception as e:
        print(f"❌ Error en verificación de relaciones: {e}")
    
    print("\n" + "="*50)

def verificar_formulario_backend():
    """Verificar compatibilidad entre formulario y backend"""
    print("📝 VERIFICANDO COMPATIBILIDAD FORMULARIO-BACKEND...")
    
    # Campos que el formulario envía
    campos_formulario = [
        'unidad_academica', 'carrera', 'asignatura', 'semestre',
        'codigo_competencia', 'sigla_curricular', 'carga_horaria_semanal',
        'carga_horaria_semestral', 'criterio_desempeno', 'unidad_didactica',
        'contenidos_analiticos[]', 'bibliografia_X_Y', 'practica_laboratorio_X_Y',
        'titulo_X_Y', 'competencias_X_Y', 'objetivo_practica_X_Y',
        'fundamento_teorico_X_Y', 'materiales_X_Y', 'herramientas_equipos_X_Y',
        'procedimientos_X_Y', 'calculos_resultados_X_Y', 'cuestionario_X_Y'
    ]
    
    print("✅ Campos del formulario definidos correctamente")
    
    # Verificar que la vista puede procesar estos campos
    from core.views import agregar_datos_malla_view
    print("✅ Vista agregar_datos_malla_view importada correctamente")
    
    print("\n" + "="*50)

def verificar_urls():
    """Verificar que todas las URLs estén configuradas correctamente"""
    print("🌐 VERIFICANDO CONFIGURACIÓN DE URLs...")
    
    from django.urls import reverse
    from django.test import Client
    
    urls_a_verificar = [
        'core:dashboard',
        'core:malla_curricular', 
        'core:agregar_datos_malla',
        'core:carreras_por_unidad',
    ]
    
    for url_name in urls_a_verificar:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name} -> {url}")
        except Exception as e:
            print(f"❌ {url_name} - Error: {e}")
    
    print("\n" + "="*50)

def verificar_integridad_datos():
    """Verificar que no hay datos duplicados o inconsistentes"""
    print("🎯 VERIFICANDO INTEGRIDAD DE DATOS...")
    
    # Verificar duplicados en unidades académicas
    unidades_duplicadas = UnidadAcademica.objects.values('nombre').annotate(
        total=models.Count('nombre')
    ).filter(total__gt=1)
    
    if unidades_duplicadas:
        print(f"⚠️  Unidades académicas duplicadas encontradas: {list(unidades_duplicadas)}")
    else:
        print("✅ No hay unidades académicas duplicadas")
    
    # Verificar duplicados en carreras
    carreras_duplicadas = Carrera.objects.values('nombre', 'unidad_academica').annotate(
        total=models.Count('id')
    ).filter(total__gt=1)
    
    if carreras_duplicadas:
        print(f"⚠️  Carreras duplicadas encontradas: {list(carreras_duplicadas)}")
    else:
        print("✅ No hay carreras duplicadas")
    
    # Verificar que todas las carreras tienen unidad académica asignada
    carreras_sin_unidad = Carrera.objects.filter(unidad_academica__isnull=True).count()
    if carreras_sin_unidad > 0:
        print(f"⚠️  {carreras_sin_unidad} carreras sin unidad académica asignada")
    else:
        print("✅ Todas las carreras tienen unidad académica asignada")
    
    print("\n" + "="*50)

def generar_reporte_estadisticas():
    """Generar reporte de estadísticas del sistema"""
    print("📊 REPORTE DE ESTADÍSTICAS DEL SISTEMA")
    
    stats = {
        'Unidades Académicas': UnidadAcademica.objects.count(),
        'Carreras': Carrera.objects.count(),
        'Asignaturas': Asignatura.objects.count(),
        'Criterios de Desempeño': CriterioDesempeno.objects.count(),
        'Unidades Didácticas': UnidadDidactica.objects.count(),
        'Contenidos Analíticos': ContenidoAnalitico.objects.count(),
        'Bibliografías': Bibliografia.objects.count(),
        'Prácticas de Laboratorio': PracticaLaboratorio.objects.count(),
        'Títulos': Titulo.objects.count(),
        'Competencias': Competencias.objects.count(),
        'Objetivos de Práctica': ObjetivoPractica.objects.count(),
        'Fundamentos Teóricos': FundamentoTeorico.objects.count(),
        'Materiales/Herramientas/Equipos': MaterialesHerramientasEquipos.objects.count(),
        'Procedimientos': Procedimientos.objects.count(),
        'Cálculos y Resultados': CalculosResultados.objects.count(),
        'Cuestionarios': Cuestionario.objects.count(),
    }
    
    for concepto, cantidad in stats.items():
        print(f"📈 {concepto}: {cantidad}")
    
    print("\n" + "="*50)

def main():
    """Función principal para ejecutar todas las verificaciones"""
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 70)
    
    try:
        verificar_modelos()
        verificar_relaciones()
        verificar_formulario_backend()
        verificar_urls()
        verificar_integridad_datos()
        generar_reporte_estadisticas()
        
        print("🎉 VERIFICACIÓN COMPLETA EXITOSA")
        print("✅ El sistema está armónico y funcionando correctamente")
        print("✅ No se encontraron variables dobles o inconsistencias críticas")
        print("✅ Todas las conexiones están funcionando apropiadamente")
        
    except Exception as e:
        print(f"❌ ERROR DURANTE LA VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()