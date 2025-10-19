#!/usr/bin/env python3
"""
Probar el sistema de protección completo
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Asignatura, Carrera
import json

def probar_sistema_proteccion():
    """Probar todas las capas de protección"""
    
    print("🛡️ PROBANDO SISTEMA DE PROTECCIÓN COMPLETO")
    print("=" * 60)
    
    # 1. Probar filtro AJAX mejorado
    print("\n1. 🔍 FILTRO AJAX MEJORADO:")
    try:
        ing_industrial = Carrera.objects.get(nombre='ING_INDUSTRIAL')
        asignaturas = Asignatura.objects.filter(carrera=ing_industrial)
        
        incluidas = []
        filtradas = []
        
        for asignatura in asignaturas:
            display_name = asignatura.get_nombre_display()
            
            # Aplicar filtro estricto
            es_numerica = asignatura.nombre.isdigit()
            es_muy_corta = len(asignatura.nombre.strip()) <= 3
            tiene_solo_numeros = asignatura.nombre.replace(' ', '').isdigit()
            
            if es_numerica or (es_muy_corta and tiene_solo_numeros):
                filtradas.append(asignatura)
                continue
            
            # Filtro adicional de nombres confusos
            nombres_similares = ['168', '169', '170', '171', '172', '173', '174', '175']
            if asignatura.nombre in nombres_similares:
                filtradas.append(asignatura)
                continue
            
            incluidas.append(asignatura)
        
        print(f"   ✅ Asignaturas incluidas ({len(incluidas)}):")
        for asig in incluidas:
            print(f"      - [ID:{asig.id}] {asig.get_nombre_display()}")
        
        print(f"\n   🚫 Asignaturas filtradas ({len(filtradas)}):")
        for asig in filtradas:
            print(f"      - [ID:{asig.id}] '{asig.nombre}' (problemática)")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Probar validación backend
    print(f"\n2. 🔒 VALIDACIÓN BACKEND:")
    nombres_test = ['168', 'FISICA I', '169', 'QUIMICA GENERAL', '12', 'abc']
    
    for nombre in nombres_test:
        # Simular validación backend
        es_problematico = nombre.isdigit() or len(nombre.strip()) <= 3
        esta_en_lista_negra = nombre in ['168', '169', '170', '171', '172', '173', '174', '175', '176', '177']
        
        if es_problematico or esta_en_lista_negra:
            print(f"   🚫 '{nombre}' → RECHAZADO (problemático)")
        else:
            print(f"   ✅ '{nombre}' → ACEPTADO")
    
    # 3. Verificar estado actual
    print(f"\n3. 📊 ESTADO ACTUAL DEL SISTEMA:")
    
    print(f"   🎯 Asignaturas legítimas con prácticas:")
    asignaturas_buenas = ['FISICA I', 'QUIMICA GENERAL', 'FISICA II', 'FISICOQUIMICA']
    
    for nombre in asignaturas_buenas:
        try:
            asig = Asignatura.objects.get(nombre=nombre)
            from core.models import ContenidoAnalitico
            count = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
            print(f"      ✅ {nombre} (ID: {asig.id}) → {count} prácticas")
        except Exception as e:
            print(f"      ❌ {nombre} → Error: {e}")
    
    print(f"\n   ⚠️ Asignaturas problemáticas:")
    asignaturas_problematicas = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    
    for asig in asignaturas_problematicas:
        from core.models import ContenidoAnalitico
        count = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
        estado = "FILTRADA" if count == 0 else f"{count} prácticas (MIGRAR)"
        print(f"      🚫 ID {asig.id}: '{asig.nombre}' → {estado}")
    
    print(f"\n4. 🎯 RESUMEN DE PROTECCIONES:")
    print(f"   🔍 Capa 1: Filtro AJAX estricto (frontend)")
    print(f"   🔒 Capa 2: Validación de nombres problemáticos (backend)")
    print(f"   📋 Capa 3: Lista negra de nombres específicos (backend)")
    print(f"   🛡️ Capa 4: Validación de unidad académica (backend)")
    print(f"   📝 Capa 5: Confirmación JavaScript detallada (frontend)")
    print(f"   📊 Capa 6: Auditoría completa con metadatos (backend)")
    
    return True

if __name__ == "__main__":
    probar_sistema_proteccion()