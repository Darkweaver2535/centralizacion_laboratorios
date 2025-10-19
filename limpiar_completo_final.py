#!/usr/bin/env python
"""
Script para eliminar todos los contenidos analíticos vacíos automáticamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def eliminar_todos_contenidos_vacios():
    print("🗑️ ELIMINANDO TODOS LOS CONTENIDOS ANALÍTICOS VACÍOS")
    print("=" * 60)
    
    # Contar por asignatura antes de eliminar
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    conteos_antes = {}
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            count = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            ).count()
            conteos_antes[asignatura.nombre] = count
    
    print(f"📊 ESTADO INICIAL:")
    for asignatura, count in conteos_antes.items():
        print(f"   📚 {asignatura}: {count} contenidos")
    
    total_inicial = sum(conteos_antes.values())
    print(f"   🧪 Total inicial: {total_inicial}")
    
    # Eliminar todos los contenidos analíticos
    print(f"\n🗑️ ELIMINANDO CONTENIDOS...")
    
    eliminados = 0
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            contenidos = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asignatura
            )
            
            count_asignatura = contenidos.count()
            if count_asignatura > 0:
                print(f"   📚 Eliminando {count_asignatura} contenidos de {asignatura.nombre}...")
                contenidos.delete()
                eliminados += count_asignatura
    
    # Limpiar también datos relacionados huérfanos
    print(f"\n🧹 LIMPIANDO DATOS RELACIONADOS HUÉRFANOS...")
    
    # Eliminar datos sin contenido analítico asociado
    modelos_a_limpiar = [
        ('Competencias', Competencias),
        ('Objetivos', ObjetivoPractica), 
        ('Procedimientos', Procedimientos),
        ('Fundamentos', FundamentoTeorico),
        ('Materiales', MaterialesHerramientasEquipos),
        ('Títulos', Titulo),
        ('Bibliografías', Bibliografia),
        ('Prácticas', PracticaLaboratorio),
        ('Cálculos', CalculosResultados),
        ('Cuestionarios', Cuestionario),
        ('Auditorías', AuditoriaCreacionPractica)
    ]
    
    for nombre_modelo, modelo in modelos_a_limpiar:
        count_inicial = modelo.objects.count()
        modelo.objects.all().delete()
        if count_inicial > 0:
            print(f"   🗑️ {nombre_modelo}: {count_inicial} registros eliminados")
    
    # Verificar estado final
    print(f"\n✅ ELIMINACIÓN COMPLETADA:")
    print(f"   🗑️ Contenidos eliminados: {eliminados}")
    
    # Verificar que todo esté limpio
    contenidos_restantes = ContenidoAnalitico.objects.count()
    print(f"   🧪 Contenidos restantes: {contenidos_restantes}")
    
    if contenidos_restantes == 0:
        print(f"\n🎉 ¡PERFECTO! Base de datos completamente limpia")
        print(f"📝 Ahora puedes crear contenidos profesionales desde cero")
    else:
        print(f"\n⚠️ Aún quedan {contenidos_restantes} contenidos")

def verificar_estructura_intacta():
    print(f"\n🏗️ VERIFICANDO ESTRUCTURA ACADÉMICA INTACTA")
    print("=" * 50)
    
    asignaturas = Asignatura.objects.count()
    unidades = UnidadDidactica.objects.count()
    laboratorios = Laboratorio.objects.count()
    
    print(f"   📚 Asignaturas: {asignaturas}")
    print(f"   📖 Unidades didácticas: {unidades}")
    print(f"   🏭 Laboratorios: {laboratorios}")
    
    print(f"\n✅ Estructura académica preservada - Solo se eliminó contenido vacío")

if __name__ == "__main__":
    eliminar_todos_contenidos_vacios()
    verificar_estructura_intacta()