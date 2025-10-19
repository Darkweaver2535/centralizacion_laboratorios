#!/usr/bin/env python
"""
Script para debuggear las validaciones del formulario
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_asignaturas_fisicoquimica():
    print("🔍 VERIFICANDO ASIGNATURAS DE FISICOQUIMICA")
    print("=" * 60)
    
    # Buscar todas las asignaturas relacionadas con fisicoquimica
    asignaturas_fisico = Asignatura.objects.filter(
        nombre__icontains='fisicoquimica'
    ).select_related('carrera')
    
    print(f"\n📚 Asignaturas con 'fisicoquimica' en el nombre:")
    for asig in asignaturas_fisico:
        print(f"   ID: {asig.id} - Nombre: '{asig.nombre}' - Carrera: {asig.carrera.nombre}")
    
    # Buscar también variaciones
    variaciones = ['fisica', 'quimica', 'fisico', 'químic']
    print(f"\n🔄 Buscando variaciones...")
    for variacion in variaciones:
        asigs = Asignatura.objects.filter(nombre__icontains=variacion).select_related('carrera')
        print(f"\n   Asignaturas con '{variacion}':")
        for asig in asigs:
            # Verificar si está en la lista negra
            es_problemática = (asig.nombre.isdigit() or 
                             len(asig.nombre.strip()) <= 3 or
                             asig.nombre in ['168', '169', '170', '171', '172', '173', '174', '175', '176', '177'])
            estado = "❌ BLOQUEADA" if es_problemática else "✅ PERMITIDA"
            print(f"      ID: {asig.id} - '{asig.nombre}' - {asig.carrera.nombre} - {estado}")

def verificar_carreras_ualp():
    print(f"\n🎓 VERIFICANDO CARRERAS EN UALP (ID: 1)")
    print("=" * 60)
    
    ualp = UnidadAcademica.objects.get(id=1)
    carreras_ualp = Carrera.objects.filter(unidad_academica=ualp)
    
    print(f"   Unidad: {ualp.nombre}")
    print(f"   Total carreras: {carreras_ualp.count()}")
    
    for carrera in carreras_ualp:
        print(f"      ID: {carrera.id} - {carrera.get_nombre_display()}")
        
        # Verificar si hay asignaturas de fisicoquimica en esta carrera
        fisico_en_carrera = Asignatura.objects.filter(
            carrera=carrera,
            nombre__icontains='fisico'
        )
        
        if fisico_en_carrera.exists():
            print(f"         🧪 Asignaturas de física/fisicoquímica:")
            for asig in fisico_en_carrera:
                es_problemática = (asig.nombre.isdigit() or 
                                 len(asig.nombre.strip()) <= 3 or
                                 asig.nombre in ['168', '169', '170', '171', '172', '173', '174', '175', '176', '177'])
                estado = "❌ BLOQUEADA" if es_problemática else "✅ PERMITIDA"
                print(f"            ID: {asig.id} - '{asig.nombre}' - {estado}")

def simular_validaciones(nombre_asignatura):
    print(f"\n🧪 SIMULANDO VALIDACIONES PARA: '{nombre_asignatura}'")
    print("=" * 60)
    
    # Validación 1: Números o muy corto
    validacion1 = nombre_asignatura.isdigit() or len(nombre_asignatura.strip()) <= 3
    print(f"   Validación 1 (isdigit o <=3 chars): {'❌ FALLA' if validacion1 else '✅ PASA'}")
    
    # Validación 2: Lista negra
    nombres_prohibidos = ['168', '169', '170', '171', '172', '173', '174', '175', '176', '177']
    validacion2 = nombre_asignatura in nombres_prohibidos
    print(f"   Validación 2 (lista negra): {'❌ FALLA' if validacion2 else '✅ PASA'}")
    
    # Resultado final
    bloqueado = validacion1 or validacion2
    print(f"   RESULTADO FINAL: {'❌ BLOQUEADO' if bloqueado else '✅ PERMITIDO'}")
    
    return not bloqueado

if __name__ == "__main__":
    verificar_asignaturas_fisicoquimica()
    verificar_carreras_ualp()
    
    # Probar algunas variaciones comunes
    nombres_prueba = [
        "FISICOQUIMICA",
        "FISICOQUÍMICA", 
        "Fisicoquimica",
        "FISICA II",
        "QUIMICA GENERAL",
        "171",  # Posible nombre problemático
        "172",  # Posible nombre problemático
    ]
    
    for nombre in nombres_prueba:
        simular_validaciones(nombre)