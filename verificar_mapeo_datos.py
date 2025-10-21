#!/usr/bin/env python3
"""
Script para verificar el mapeo de datos en la plantilla EMI
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import PracticaLaboratorio
from guias.plantilla_utils import crear_guia_temporal_desde_practica, preparar_contexto_plantilla
from usuarios.models import Usuario

def verificar_mapeo_datos():
    """Verificar que todos los datos se mapeen correctamente"""
    
    print("🔍 === VERIFICACIÓN DE MAPEO DE DATOS ===")
    
    # Obtener práctica de ejemplo
    practica = PracticaLaboratorio.objects.get(id=22)
    print(f"📋 Práctica: {practica.nombre}")
    
    # Obtener usuario
    usuario = Usuario.objects.first()
    
    # Crear guía temporal
    guia_temporal = crear_guia_temporal_desde_practica(practica, usuario)
    print(f"✅ Guía temporal creada: {guia_temporal.titulo}")
    
    # Preparar contexto
    contexto = preparar_contexto_plantilla(guia_temporal)
    
    # Verificar campos específicos que estaban faltando
    campos_criticos = [
        'codigo',
        'version',
        'docente',
        'contenido_analitico',
        'unidad_didactica',
        'procedimiento',
        'cálculos_resultados',
        'cuestionario',
        'fundamento_teorico',
        'bibliografía'
    ]
    
    print(f"\n📊 === VERIFICACIÓN DE CAMPOS CRÍTICOS ===")
    for campo in campos_criticos:
        valor = contexto.get(campo, 'NO ENCONTRADO')
        print(f"  ✓ {campo}: {valor[:100]}{'...' if len(str(valor)) > 100 else ''}")
    
    # Verificar equipos, materiales, herramientas
    print(f"\n🔧 === VERIFICACIÓN DE RECURSOS ===")
    
    for i in range(1, 4):
        equipo = contexto.get(f'equipo{i}', '')
        cantidad_equipo = contexto.get(f'cantidad_equipo{i}', '')
        if equipo:
            print(f"  ✓ Equipo {i}: {equipo} (Cantidad: {cantidad_equipo})")
        else:
            print(f"  ⚠️ Equipo {i}: No disponible")
    
    for i in range(1, 4):
        material = contexto.get(f'material{i}', '')
        cantidad_material = contexto.get(f'cantidad_material{i}', '')
        if material:
            print(f"  ✓ Material {i}: {material} (Cantidad: {cantidad_material})")
        else:
            print(f"  ⚠️ Material {i}: No disponible")
    
    for i in range(1, 7):
        herramienta = contexto.get(f'herramienta{i}', '')
        cantidad_herramienta = contexto.get(f'cantidad_herramienta{i}', '')
        if herramienta:
            print(f"  ✓ Herramienta {i}: {herramienta} (Cantidad: {cantidad_herramienta})")
        else:
            print(f"  ⚠️ Herramienta {i}: No disponible")
    
    # Contar campos vacíos vs llenos
    campos_llenos = sum(1 for k, v in contexto.items() if v and str(v).strip())
    campos_vacios = sum(1 for k, v in contexto.items() if not v or not str(v).strip())
    
    print(f"\n📈 === ESTADÍSTICAS ===")
    print(f"  ✅ Campos con datos: {campos_llenos}")
    print(f"  ⚠️ Campos vacíos: {campos_vacios}")
    print(f"  📊 Total campos: {len(contexto)}")
    print(f"  🎯 Porcentaje completo: {(campos_llenos / len(contexto) * 100):.1f}%")
    
    # Mostrar todos los campos disponibles
    print(f"\n📋 === TODOS LOS CAMPOS MAPEADOS ({len(contexto)}) ===")
    for key, value in sorted(contexto.items()):
        status = "✅" if value and str(value).strip() else "❌"
        print(f"  {status} {key}: {str(value)[:80]}{'...' if len(str(value)) > 80 else ''}")
    
    return campos_llenos > campos_vacios

if __name__ == '__main__':
    success = verificar_mapeo_datos()
    
    if success:
        print("\n🎉 ¡MAPEO EXITOSO! La mayoría de campos tienen datos.")
    else:
        print("\n⚠️ Mapeo incompleto. Revisar campos faltantes.")
    
    sys.exit(0 if success else 1)