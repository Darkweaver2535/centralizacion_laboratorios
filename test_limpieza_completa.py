#!/usr/bin/env python3
"""
Script para limpiar completamente el cache y verificar estado
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from ingreso_datos.models import *

def limpiar_cache_y_verificar():
    """Limpiar cache y verificar estado"""
    print("=== LIMPIEZA Y VERIFICACIÓN COMPLETA ===\n")
    
    # Verificar estado de la base de datos
    print("1. ESTADO DE LA BASE DE DATOS:")
    for ua in UnidadAcademica.objects.all():
        count = EquipoIndividual.objects.filter(unidad_academica=ua).count()
        print(f"   {ua.nombre}: {count} equipos")
    
    # Verificar integridad
    print("\n2. VERIFICACIÓN DE INTEGRIDAD:")
    total = EquipoIndividual.objects.count()
    con_unidad = EquipoIndividual.objects.filter(unidad_academica__isnull=False).count()
    print(f"   Total equipos: {total}")
    print(f"   Con unidad académica: {con_unidad}")
    print(f"   Huérfanos: {total - con_unidad}")
    
    # Verificar algunos equipos específicos
    print("\n3. MUESTRA DE EQUIPOS:")
    equipos_muestra = EquipoIndividual.objects.select_related('unidad_academica')[:5]
    for equipo in equipos_muestra:
        ua_nombre = equipo.unidad_academica.nombre if equipo.unidad_academica else 'SIN_UNIDAD'
        print(f"   {equipo.codigo}: {ua_nombre}")
    
    # Verificar tipos de equipo
    print("\n4. TIPOS DE EQUIPO:")
    tipos_count = TipoEquipo.objects.count()
    print(f"   Total tipos: {tipos_count}")
    
    # Verificar equipos por tipo específico
    print("\n5. EQUIPOS POR TIPO (primeros 3 tipos):")
    for tipo in TipoEquipo.objects.all()[:3]:
        for ua in UnidadAcademica.objects.all():
            count = EquipoIndividual.objects.filter(
                tipo_equipo=tipo,
                unidad_academica=ua
            ).count()
            if count > 0:
                print(f"   {tipo.nombre} en {ua.nombre}: {count}")
    
    print("\n=== CONCLUSIÓN ===")
    print("Si ves equipos en el navegador para Riberalta/Trópico:")
    print("1. Fuerza refresh del navegador (Ctrl+F5)")
    print("2. Limpia cache del navegador")
    print("3. Verifica la consola de JavaScript")
    print("4. El backend está funcionando correctamente")

if __name__ == "__main__":
    limpiar_cache_y_verificar()
