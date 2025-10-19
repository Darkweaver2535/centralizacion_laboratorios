#!/usr/bin/env python
"""
Script para verificar el estado completo de la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_estado_completo():
    print("🔍 VERIFICACIÓN COMPLETA DEL ESTADO DE LA BASE DE DATOS")
    print("=" * 70)
    
    # Verificar asignaturas principales
    asignaturas_principales = ['FISICA I', 'FISICA II', 'QUIMICA GENERAL', 'FISICOQUIMICA']
    
    print(f"\n📚 ESTADO POR ASIGNATURA:")
    for nombre_asig in asignaturas_principales:
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if asignatura:
            print(f"\n   📖 {asignatura.nombre}:")
            
            # Unidades didácticas
            unidades = UnidadDidactica.objects.filter(asignatura=asignatura)
            print(f"      📋 Unidades didácticas: {unidades.count()}")
            
            # Contenidos analíticos
            contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asignatura)
            print(f"      🧪 Contenidos analíticos: {contenidos.count()}")
            
            if contenidos.count() > 0:
                print(f"      ⚠️ CONTENIDOS ENCONTRADOS:")
                for contenido in contenidos[:5]:  # Mostrar solo los primeros 5
                    print(f"         - '{contenido.nombre}' en {contenido.unidad_didactica.nombre}")
                if contenidos.count() > 5:
                    print(f"         ... y {contenidos.count() - 5} más")
    
    # Verificar todos los modelos relacionados
    print(f"\n🔍 VERIFICACIÓN DE MODELOS RELACIONADOS:")
    
    modelos_verificar = [
        ('ContenidoAnalitico', ContenidoAnalitico),
        ('Competencias', Competencias),
        ('ObjetivoPractica', ObjetivoPractica),
        ('Procedimientos', Procedimientos),
        ('FundamentoTeorico', FundamentoTeorico),
        ('MaterialesHerramientasEquipos', MaterialesHerramientasEquipos),
        ('Titulo', Titulo),
        ('Bibliografia', Bibliografia),
        ('PracticaLaboratorio', PracticaLaboratorio),
        ('CalculosResultados', CalculosResultados),
        ('Cuestionario', Cuestionario),
        ('AuditoriaCreacionPractica', AuditoriaCreacionPractica)
    ]
    
    total_registros = 0
    for nombre_modelo, modelo in modelos_verificar:
        count = modelo.objects.count()
        total_registros += count
        if count > 0:
            print(f"   ⚠️ {nombre_modelo}: {count} registros")
        else:
            print(f"   ✅ {nombre_modelo}: 0 registros")
    
    # Estructura académica (debe mantenerse intacta)
    print(f"\n🏗️ ESTRUCTURA ACADÉMICA (DEBE MANTENERSE):")
    print(f"   📚 Asignaturas: {Asignatura.objects.count()}")
    print(f"   📖 Unidades didácticas: {UnidadDidactica.objects.count()}")
    print(f"   🏭 Laboratorios: {Laboratorio.objects.count()}")
    # print(f"   👥 Responsables: {Responsable.objects.count()}")
    print(f"   📝 Carreras: {Carrera.objects.count()}")
    print(f"   🏢 Unidades académicas: {UnidadAcademica.objects.count()}")
    
    # Resumen final
    print(f"\n📊 RESUMEN FINAL:")
    if total_registros == 0:
        print(f"   🎉 ¡PERFECTO! Base de datos limpia para uso profesional")
        print(f"   ✅ 0 contenidos de prueba restantes")
        print(f"   🏗️ Estructura académica intacta y lista")
    else:
        print(f"   ⚠️ Aún hay {total_registros} registros de contenido")
        print(f"   🧹 Se requiere limpieza adicional")

if __name__ == "__main__":
    verificar_estado_completo()