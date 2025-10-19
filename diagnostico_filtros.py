#!/usr/bin/env python3

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera, UnidadAcademica
from core.filters import AsignaturaFilter
from django.http import QueryDict

def probar_filtros_asignaturas():
    """Probar el funcionamiento de los filtros de asignaturas"""
    
    print("=== DIAGNÓSTICO DE FILTROS DE ASIGNATURAS ===")
    
    # 1. Verificar datos base
    print(f"1. Total asignaturas: {Asignatura.objects.count()}")
    print(f"2. Total carreras: {Carrera.objects.count()}")
    print(f"3. Total unidades: {UnidadAcademica.objects.count()}")
    
    # 2. Verificar asignaturas limpias (sin nombres numéricos)
    asignaturas_validas = []
    for asig in Asignatura.objects.all():
        if not asig.nombre.isdigit():
            asignaturas_validas.append(asig.id)
    
    print(f"4. Asignaturas válidas (sin nombres numéricos): {len(asignaturas_validas)}")
    
    # 3. Probar filtros básicos
    print("\n=== PROBANDO FILTROS ===")
    
    # Base queryset (como en la vista)
    try:
        ualp = UnidadAcademica.objects.get(id=1, nombre='UALP')
        base_queryset = Asignatura.objects.filter(
            id__in=asignaturas_validas,
            carrera__unidad_academica=ualp
        ).select_related('carrera', 'carrera__unidad_academica')
        
        print(f"5. Asignaturas de UALP válidas: {base_queryset.count()}")
        
        # Probar filtros uno por uno
        filtros_prueba = [
            {"search": "FISICA"},
            {"carrera": "23"},  # Ing. Industrial
            {"semestre": "1"},
            {"search": "QUIMICA"},
        ]
        
        for i, filtro_data in enumerate(filtros_prueba, 1):
            print(f"\n--- FILTRO {i}: {filtro_data} ---")
            
            # Crear QueryDict simulando GET request
            query_dict = QueryDict(mutable=True)
            for key, value in filtro_data.items():
                query_dict[key] = value
            
            # Aplicar filtro
            filterset = AsignaturaFilter(query_dict, queryset=base_queryset)
            resultados = filterset.qs
            
            print(f"Resultados encontrados: {resultados.count()}")
            
            for asig in resultados[:5]:  # Mostrar primeros 5
                print(f"  - ID {asig.id}: {asig.nombre} ({asig.carrera.nombre})")
                
            if resultados.count() > 5:
                print(f"  ... y {resultados.count() - 5} más")
    
    except UnidadAcademica.DoesNotExist:
        print("ERROR: No se encontró UALP")
        return False
    
    # 4. Verificar filtros en carreras
    print(f"\n=== VERIFICANDO CARRERAS DISPONIBLES ===")
    
    try:
        ualp = UnidadAcademica.objects.get(id=1)
        carreras_ualp = Carrera.objects.filter(unidad_academica=ualp)
        print(f"Carreras de UALP: {carreras_ualp.count()}")
        
        for carrera in carreras_ualp[:10]:  # Primeras 10
            asig_count = Asignatura.objects.filter(
                carrera=carrera,
                id__in=asignaturas_validas
            ).count()
            print(f"  - {carrera.nombre}: {asig_count} asignaturas")
            
    except Exception as e:
        print(f"ERROR en carreras: {e}")
    
    return True

def probar_filtro_cascada():
    """Probar filtros en cascada (unidad -> carrera)"""
    
    print(f"\n=== PROBANDO FILTROS EN CASCADA ===")
    
    try:
        # Simular selección de UALP
        ualp = UnidadAcademica.objects.get(id=1)
        carreras = Carrera.objects.filter(unidad_academica=ualp)
        
        print(f"Al seleccionar UALP, deberían aparecer {carreras.count()} carreras:")
        for carrera in carreras:
            print(f"  - {carrera.nombre}")
        
        # Simular selección de Ing. Industrial
        ing_industrial = carreras.filter(nombre__icontains='INDUSTRIAL').first()
        if ing_industrial:
            print(f"\nAl seleccionar {ing_industrial.nombre}:")
            
            asignaturas = Asignatura.objects.filter(carrera=ing_industrial)
            asignaturas_validas = [asig for asig in asignaturas if not asig.nombre.isdigit()]
            
            print(f"  - Deberían aparecer {len(asignaturas_validas)} asignaturas")
            
            # Agrupar por semestre
            por_semestre = {}
            for asig in asignaturas_validas:
                sem = asig.semestre or 'Sin semestre'
                if sem not in por_semestre:
                    por_semestre[sem] = []
                por_semestre[sem].append(asig)
            
            for semestre, asigs in sorted(por_semestre.items()):
                print(f"    Semestre {semestre}: {len(asigs)} asignaturas")
                
    except Exception as e:
        print(f"ERROR en cascada: {e}")

if __name__ == "__main__":
    if probar_filtros_asignaturas():
        probar_filtro_cascada()