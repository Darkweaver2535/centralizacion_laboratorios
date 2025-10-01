#!/usr/bin/env python
"""
Script para verificar los datos existentes para R2
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, UnidadDidactica, ContenidoAnalitico, Laboratorio
from equipos.models import Equipo
from insumos.models import Insumo
from guias.models import GuiaGenerada

def verificar_datos():
    print("=== VERIFICACIÓN DE DATOS PARA FILTROS DINÁMICOS R2 ===\n")
    
    # Verificar Unidades Académicas
    unidades = UnidadAcademica.objects.all()
    print(f"📚 Unidades Académicas: {unidades.count()}")
    for unidad in unidades[:5]:  # Mostrar primeras 5
        print(f"   - {unidad.nombre}")
    if unidades.count() > 5:
        print(f"   ... y {unidades.count() - 5} más\n")
    else:
        print()
    
    # Verificar Carreras
    carreras = Carrera.objects.all()
    print(f"🎓 Carreras: {carreras.count()}")
    for carrera in carreras[:5]:
        print(f"   - {carrera.nombre} (Unidad: {carrera.unidad_academica.nombre if carrera.unidad_academica else 'Sin unidad'})")
    if carreras.count() > 5:
        print(f"   ... y {carreras.count() - 5} más\n")
    else:
        print()
    
    # Verificar Asignaturas
    asignaturas = Asignatura.objects.all()
    print(f"📖 Asignaturas: {asignaturas.count()}")
    for asignatura in asignaturas[:5]:
        print(f"   - {asignatura.nombre}")
    if asignaturas.count() > 5:
        print(f"   ... y {asignaturas.count() - 5} más\n")
    else:
        print()
    
    # Verificar relaciones Asignatura-Carrera-Semestre (a través del modelo Asignatura)
    asignaturas_con_carrera = Asignatura.objects.filter(carrera__isnull=False)
    print(f"🗓️ Asignaturas con Carrera-Semestre: {asignaturas_con_carrera.count()}")
    for asig in asignaturas_con_carrera[:5]:
        print(f"   - {asig.nombre} | {asig.carrera.nombre} | Sem: {asig.semestre}")
    if asignaturas_con_carrera.count() > 5:
        print(f"   ... y {asignaturas_con_carrera.count() - 5} más\n")
    else:
        print()
    
    # Verificar Unidades Didácticas
    unidades_didacticas = UnidadDidactica.objects.all()
    print(f"📚 Unidades Didácticas: {unidades_didacticas.count()}")
    for ud in unidades_didacticas[:5]:
        asignatura_nombre = ud.asignatura.nombre if ud.asignatura else 'Sin asignatura'
        print(f"   - {ud.nombre} (Asignatura: {asignatura_nombre})")
    if unidades_didacticas.count() > 5:
        print(f"   ... y {unidades_didacticas.count() - 5} más\n")
    else:
        print()
    
    # Verificar Contenidos Analíticos
    contenidos = ContenidoAnalitico.objects.all()
    print(f"🔬 Contenidos Analíticos: {contenidos.count()}")
    for contenido in contenidos[:5]:
        ud_nombre = contenido.unidad_didactica.nombre if contenido.unidad_didactica else 'Sin UD'
        print(f"   - {contenido.nombre} (UD: {ud_nombre})")
    if contenidos.count() > 5:
        print(f"   ... y {contenidos.count() - 5} más\n")
    else:
        print()
    
    # Verificar Equipos
    equipos = Equipo.objects.all()
    print(f"🔧 Equipos: {equipos.count()}")
    estados = equipos.values_list('estado', flat=True).distinct()
    print(f"   Estados disponibles: {list(estados)}")
    for estado in estados:
        count = equipos.filter(estado=estado).count()
        print(f"   - {estado}: {count} equipos")
    print()
    
    # Verificar Insumos
    insumos = Insumo.objects.all()
    print(f"🧪 Insumos: {insumos.count()}")
    for insumo in insumos[:5]:
        print(f"   - {insumo.nombre}")
    if insumos.count() > 5:
        print(f"   ... y {insumos.count() - 5} más\n")
    else:
        print()
    
    # Verificar Guías de Laboratorio (GuiaGenerada)
    guias = GuiaGenerada.objects.all()
    print(f"📋 Guías de Laboratorio: {guias.count()}")
    if guias.count() > 0:
        estados_guias = guias.values_list('estado', flat=True).distinct()
        print(f"   Estados disponibles: {list(estados_guias)}")
        for estado in estados_guias:
            count = guias.filter(estado=estado).count()
            print(f"   - {estado}: {count} guías")
    else:
        print("   No hay guías generadas")
    print()
    
    # Verificar Laboratorios
    laboratorios = Laboratorio.objects.all()
    print(f"🏫 Laboratorios: {laboratorios.count()}")
    for lab in laboratorios[:5]:
        print(f"   - {lab.nombre}")
    if laboratorios.count() > 5:
        print(f"   ... y {laboratorios.count() - 5} más")
    
    print("\n=== RESUMEN DE RELACIONES PARA FILTROS ===")
    print(f"✅ Cascada Unidad → Carrera: {carreras.exclude(unidad_academica=None).count()}/{carreras.count()}")
    print(f"✅ Cascada Carrera → Asignatura: {asignaturas_con_carrera.count()} relaciones")
    print(f"✅ Cascada Asignatura → Unidad Didáctica: {unidades_didacticas.exclude(asignatura=None).count()}/{unidades_didacticas.count()}")
    print(f"✅ Cascada UD → Contenido: {contenidos.exclude(unidad_didactica=None).count()}/{contenidos.count()}")
    
    if asignaturas_con_carrera.count() == 0:
        print("\n⚠️  ADVERTENCIA: No hay asignaturas asociadas a carreras. Los filtros de carrera→asignatura no funcionarán.")
    
    if unidades_didacticas.exclude(asignatura=None).count() == 0:
        print("\n⚠️  ADVERTENCIA: No hay Unidades Didácticas asociadas a Asignaturas.")
    
    if contenidos.exclude(unidad_didactica=None).count() == 0:
        print("\n⚠️  ADVERTENCIA: No hay Contenidos asociados a Unidades Didácticas.")

if __name__ == "__main__":
    verificar_datos()