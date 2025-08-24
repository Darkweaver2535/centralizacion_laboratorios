#!/usr/bin/env python
"""
Script para actualizar las categorías de insumos a las 3 opciones simplificadas:
- reactivos
- materiales  
- herramientas
"""

import os
import django
from django.db import transaction

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from insumos.models import Insumo

def actualizar_categorias():
    """Actualizar categorías existentes al nuevo formato simplificado"""
    print("🔄 Actualizando categorías de insumos...")
    
    # Mapeo de categorías antiguas a nuevas
    mapeo_categorias = {
        'reactivos': 'reactivos',
        'materiales_laboratorio': 'materiales',
        'herramientas': 'herramientas',
        'consumibles': 'materiales',
        'material_vidrio': 'materiales',
        'equipos_proteccion': 'materiales',
        'material_electronico': 'materiales',
        'software': 'herramientas',
        'licencias': 'herramientas',
        'otros': 'materiales',
    }
    
    actualizados = 0
    
    with transaction.atomic():
        for categoria_antigua, categoria_nueva in mapeo_categorias.items():
            # Contar cuántos registros tienen esta categoría
            count = Insumo.objects.filter(categoria=categoria_antigua).count()
            
            if count > 0:
                # Actualizar todos los registros de esta categoría
                Insumo.objects.filter(categoria=categoria_antigua).update(categoria=categoria_nueva)
                print(f"  ✅ {count} insumos: '{categoria_antigua}' → '{categoria_nueva}'")
                actualizados += count
    
    print(f"\n✅ {actualizados} registros actualizados exitosamente")
    return actualizados

def verificar_categorias():
    """Verificar el estado de las categorías después de la actualización"""
    print("\n🔍 VERIFICACIÓN DE CATEGORÍAS:")
    print("=" * 40)
    
    # Contar por categoría
    categorias_count = {}
    for categoria, _ in Insumo.CATEGORIAS:
        count = Insumo.objects.filter(categoria=categoria).count()
        categorias_count[categoria] = count
        print(f"📦 {categoria.title()}: {count} insumos")
    
    # Verificar si hay categorías no válidas
    total_insumos = Insumo.objects.count()
    total_contado = sum(categorias_count.values())
    
    if total_contado != total_insumos:
        print(f"\n⚠️  ADVERTENCIA: Hay {total_insumos - total_contado} insumos con categorías no válidas")
        
        # Buscar categorías inválidas
        categorias_validas = [cat[0] for cat in Insumo.CATEGORIAS]
        insumos_invalidos = Insumo.objects.exclude(categoria__in=categorias_validas)
        
        if insumos_invalidos.exists():
            print("🔍 Categorías inválidas encontradas:")
            categorias_invalidas = insumos_invalidos.values_list('categoria', flat=True).distinct()
            for cat in categorias_invalidas:
                count = insumos_invalidos.filter(categoria=cat).count()
                print(f"  ❌ '{cat}': {count} insumos")
    else:
        print(f"\n✅ Todas las categorías están correctas ({total_contado} insumos)")

def main():
    """Función principal"""
    print("🚀 SIMPLIFICACIÓN DE CATEGORÍAS DE INSUMOS")
    print("=" * 50)
    
    try:
        # Verificar estado inicial
        total_inicial = Insumo.objects.count()
        print(f"📊 Total de insumos en base de datos: {total_inicial}")
        
        if total_inicial == 0:
            print("ℹ️  No hay insumos en la base de datos para actualizar")
            return
        
        # Actualizar categorías
        actualizados = actualizar_categorias()
        
        # Verificar resultado
        verificar_categorias()
        
        print("\n🎯 RESUMEN:")
        print("-" * 30)
        print("✅ Nuevas categorías disponibles:")
        for codigo, nombre in Insumo.CATEGORIAS:
            print(f"   • {codigo} → {nombre}")
        
        print(f"\n✅ {actualizados} insumos actualizados exitosamente")
        print("💡 Las categorías ahora son más simples y fáciles de usar")
        
    except Exception as e:
        print(f"❌ Error durante la actualización: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
