#!/usr/bin/env python3
"""
Script para mostrar los insumos importados en formato de tabla de 19 columnas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from insumos.models import Insumo

def mostrar_tabla_insumos():
    """Mostrar insumos en formato tabla con 19 columnas"""
    
    # Obtener todos los insumos
    insumos = Insumo.objects.all().order_by('id')[:10]  # Mostrar primeros 10
    
    print("🔍 MOSTRANDO PRIMEROS 10 INSUMOS EN FORMATO TABLA (19 COLUMNAS)")
    print("=" * 120)
    
    # Headers de las 19 columnas (ajustadas al modelo real)
    headers = [
        "UNIDAD ACADÉMICA", "LABORATORIO", "CATEGORÍA", "NOMBRE DEL ELEMENTO",
        "DESCRIPCIÓN/CARACTERÍSTICAS", "MARCA/MODELO", "CÓDIGO DE INVENTARIO",
        "ESTADO", "UBICACIÓN FÍSICA", "CANTIDAD", "UNIDAD DE MEDIDA",
        "FECHA DE INGRESO/COMPRA", "USO PRINCIPAL", "CARRERA", "ASIGNATURA",
        "UNIDAD TEMÁTICA", "CONDICIONES DE ALMACENAMIENTO", "OBSERVACIONES",
        "LINK FOTOGRAFÍA"
    ]
    
    # Mostrar headers
    print(f"{'No.':<3} | " + " | ".join([f"{h:<15}" for h in headers[:5]]))
    print("-" * 120)
    
    for i, insumo in enumerate(insumos, 1):
        # Preparar datos con "-" para campos vacíos
        datos = [
            insumo.unidad_academica.nombre if insumo.unidad_academica else "-",
            insumo.laboratorio.nombre if insumo.laboratorio else "-",
            insumo.get_categoria_display() or "-",
            insumo.nombre_elemento or "-",
            insumo.descripcion_caracteristicas[:15] + "..." if insumo.descripcion_caracteristicas and len(insumo.descripcion_caracteristicas) > 15 else insumo.descripcion_caracteristicas or "-",
            insumo.marca_modelo[:15] + "..." if insumo.marca_modelo and len(insumo.marca_modelo) > 15 else insumo.marca_modelo or "-",
            insumo.codigo_inventario or "-",
            insumo.get_estado_display() or "-",
            insumo.ubicacion_fisica[:15] + "..." if insumo.ubicacion_fisica and len(insumo.ubicacion_fisica) > 15 else insumo.ubicacion_fisica or "-",
            str(insumo.cantidad) if insumo.cantidad else "-",
            insumo.get_unidad_medida_display() or "-",
            insumo.fecha_ingreso_compra.strftime("%Y-%m-%d") if insumo.fecha_ingreso_compra else "-",
            insumo.get_uso_principal_display() or "-",
            insumo.carrera.nombre if insumo.carrera else "-",
            insumo.asignatura.nombre if insumo.asignatura else "-",
            insumo.unidad_tematica.nombre if insumo.unidad_tematica else "-",
            insumo.get_condiciones_almacenamiento_display() or "-",
            insumo.observaciones[:15] + "..." if insumo.observaciones and len(insumo.observaciones) > 15 else insumo.observaciones or "-",
            insumo.link_fotografia[:30] + "..." if insumo.link_fotografia and len(insumo.link_fotografia) > 30 else insumo.link_fotografia or "-"
        ]
        
        # Mostrar fila
        print(f"{i:<3} | " + " | ".join([f"{d:<15}" for d in datos[:5]]))
    
    print("\n📊 ESTADÍSTICAS:")
    total = Insumo.objects.count()
    print(f"✅ Total insumos importados: {total}")
    
    # Contar por categoría
    from django.db.models import Count
    categorias = Insumo.objects.values('categoria').annotate(count=Count('categoria')).order_by('-count')
    print(f"\n📋 DISTRIBUCIÓN POR CATEGORÍA:")
    for cat in categorias:
        print(f"  - {cat['categoria']}: {cat['count']} insumos")
    
    # Contar por unidad académica
    unidades = Insumo.objects.values('unidad_academica__nombre').annotate(count=Count('unidad_academica')).order_by('-count')
    print(f"\n🏛️ DISTRIBUCIÓN POR UNIDAD ACADÉMICA:")
    for uni in unidades:
        print(f"  - {uni['unidad_academica__nombre']}: {uni['count']} insumos")

if __name__ == "__main__":
    mostrar_tabla_insumos()
