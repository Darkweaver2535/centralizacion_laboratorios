#!/usr/bin/env python3
"""
Script para actualizar unidades académicas según datos reales y corregir errores
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica
from equipos.models import Equipo
from django.db import transaction

def actualizar_unidades_academicas():
    """Actualizar unidades académicas según datos reales del Excel"""
    
    print("🏫 ACTUALIZANDO UNIDADES ACADÉMICAS")
    print("=" * 40)
    
    with transaction.atomic():
        print(f"📋 Estado inicial:")
        for ua in UnidadAcademica.objects.all():
            equipos_count = Equipo.objects.filter(unidad_academica=ua).count()
            print(f"   {ua.nombre}: {equipos_count} equipos")
        
        # 1. Corregir UCRB por UARB
        try:
            ucrb = UnidadAcademica.objects.get(nombre='UCRB')
            ucrb.nombre = 'UARB'
            ucrb.descripcion = 'Universidad Autónoma del Beni José Ballivián - Regional Riberalta'
            ucrb.save()
            print(f"\n✅ Corregido: UCRB → UARB")
        except UnidadAcademica.DoesNotExist:
            print(f"\n⚠️ UCRB no encontrada")
        
        # 2. Verificar datos del Excel importado para distribución
        # Vamos a verificar si hay equipos que deberían estar en otras unidades
        
        # Analizar responsables para determinar posible distribución
        responsables_por_sede = {
            'COCHABAMBA': ['UACB'],
            'LA PAZ': ['UALP'], 
            'SANTA CRUZ': ['UASC'],
            'TARIJA': ['UATP'],
            'RIBERALTA': ['UARB'],
            'BENI': ['UARB']
        }
        
        print(f"\n🔍 Analizando responsables para detectar sedes:")
        
        # Como todos los equipos están en UALP, vamos a mantenerlos ahí
        # pero verificar si hay indicios de otras sedes en los datos
        
        equipos_ualp = Equipo.objects.filter(unidad_academica__nombre='UALP')
        responsables_unicos = equipos_ualp.values_list('responsable_excel', flat=True).distinct()
        
        print(f"\n📊 Análisis de responsables (primeros 10):")
        for i, resp in enumerate(list(responsables_unicos)[:10], 1):
            if resp:
                equipos_count = equipos_ualp.filter(responsable_excel=resp).count()
                print(f"   {i:2d}. {resp}: {equipos_count} equipos")
        
        # Limpiar unidades académicas sin equipos (excepto las principales)
        unidades_principales = ['UALP', 'UARB']  # Mantener estas
        
        print(f"\n🧹 Limpiando unidades académicas sin equipos:")
        for ua in UnidadAcademica.objects.all():
            equipos_count = Equipo.objects.filter(unidad_academica=ua).count()
            if equipos_count == 0 and ua.nombre not in unidades_principales:
                print(f"   ❌ Eliminando: {ua.nombre} (0 equipos)")
                ua.delete()
            else:
                print(f"   ✅ Manteniendo: {ua.nombre} ({equipos_count} equipos)")
        
        print(f"\n📊 ESTADO FINAL:")
        for ua in UnidadAcademica.objects.all():
            equipos_count = Equipo.objects.filter(unidad_academica=ua).count()
            print(f"   🏫 {ua.nombre}: {equipos_count} equipos")
            if ua.descripcion:
                print(f"      📝 {ua.descripcion}")
        
        print(f"\n✅ ACTUALIZACIÓN COMPLETADA")
        print(f"   Los filtros ahora mostrarán solo unidades con equipos")

if __name__ == "__main__":
    actualizar_unidades_academicas()
