#!/usr/bin/env python3
"""
Investigar problemas en el formulario de agregar datos
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import ContenidoAnalitico, AuditoriaCreacionPractica
from datetime import datetime, timedelta

def investigar_problema_formulario():
    """Investigar por qué el formulario no está guardando"""
    
    print("🔍 INVESTIGANDO PROBLEMA DEL FORMULARIO")
    print("=" * 50)
    
    # 1. Verificar últimas auditorías
    print("\n1. 📋 ÚLTIMAS AUDITORÍAS (últimos 60 minutos):")
    hace_60_min = datetime.now() - timedelta(minutes=60)
    
    try:
        auditorias_recientes = AuditoriaCreacionPractica.objects.filter(
            created_at__gte=hace_60_min
        ).order_by('-created_at')
        
        if auditorias_recientes.exists():
            for auditoria in auditorias_recientes:
                print(f"   📝 '{auditoria.practica_nombre}' → {auditoria.asignatura_nombre}")
                print(f"      👤 Usuario: {auditoria.usuario}")
                print(f"      📅 Creado: {auditoria.created_at}")
        else:
            print("   ❌ No hay auditorías recientes")
    except Exception as e:
        print(f"   ❌ Error consultando auditorías: {e}")
    
    # 2. Verificar últimos contenidos
    print("\n2. 🕒 ÚLTIMOS CONTENIDOS CREADOS (últimos 60 minutos):")
    
    try:
        ultimos_contenidos = ContenidoAnalitico.objects.filter(
            created_at__gte=hace_60_min
        ).order_by('-created_at')
        
        if ultimos_contenidos.exists():
            for contenido in ultimos_contenidos:
                asig = contenido.unidad_didactica.asignatura
                print(f"   📝 '{contenido.nombre}' → {asig.nombre} (ID: {asig.id})")
                print(f"      📅 Creado: {contenido.created_at}")
        else:
            print("   ❌ No hay contenidos creados recientemente")
    except Exception as e:
        print(f"   ❌ Error consultando contenidos: {e}")
    
    # 3. Buscar específicamente LABUBU 4
    print("\n3. 🔍 BUSCANDO 'LABUBU 4':")
    
    try:
        labubu4_contenidos = ContenidoAnalitico.objects.filter(
            nombre__icontains='LABUBU 4'
        ).select_related('unidad_didactica__asignatura')
        
        if labubu4_contenidos.exists():
            for contenido in labubu4_contenidos:
                asig = contenido.unidad_didactica.asignatura
                print(f"   ✅ Encontrado: '{contenido.nombre}'")
                print(f"      📚 Asignatura: {asig.nombre} (ID: {asig.id})")
                print(f"      📅 Creado: {contenido.created_at}")
        else:
            print("   ❌ 'LABUBU 4' no encontrado")
    except Exception as e:
        print(f"   ❌ Error buscando LABUBU 4: {e}")
    
    # 4. Buscar en títulos
    print("\n4. 🏷️ BUSCANDO EN TÍTULOS:")
    
    try:
        from core.models import Titulo
        labubu4_titulos = Titulo.objects.filter(
            texto__icontains='LABUBU 4'
        ).select_related('contenido_analitico__unidad_didactica__asignatura')
        
        if labubu4_titulos.exists():
            for titulo in labubu4_titulos:
                contenido = titulo.contenido_analitico
                asig = contenido.unidad_didactica.asignatura
                print(f"   ✅ Título encontrado: '{titulo.texto}'")
                print(f"      📝 En contenido: '{contenido.nombre}'")
                print(f"      📚 Asignatura: {asig.nombre} (ID: {asig.id})")
        else:
            print("   ❌ Título 'LABUBU 4' no encontrado")
    except Exception as e:
        print(f"   ❌ Error buscando títulos: {e}")
    
    # 5. Verificar estado de FISICOQUIMICA
    print("\n5. 🧪 VERIFICANDO FISICOQUIMICA:")
    
    try:
        from core.models import Asignatura
        fisicoquimica = Asignatura.objects.get(nombre='FISICOQUIMICA')
        contenidos_fq = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=fisicoquimica
        ).order_by('-created_at')[:5]
        
        print(f"   ✅ FISICOQUIMICA (ID: {fisicoquimica.id})")
        print(f"   📊 Total contenidos: {ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=fisicoquimica).count()}")
        print(f"   📌 Últimos 5 contenidos:")
        
        for i, contenido in enumerate(contenidos_fq, 1):
            print(f"      {i}. '{contenido.nombre}' - {contenido.created_at}")
            
    except Asignatura.DoesNotExist:
        print("   ❌ FISICOQUIMICA no encontrada")
    except Exception as e:
        print(f"   ❌ Error verificando FISICOQUIMICA: {e}")
    
    # 6. Diagnóstico del problema
    print("\n6. 🚨 DIAGNÓSTICO DEL PROBLEMA:")
    print("   Posibles causas del fallo en el formulario:")
    print("   1. ❌ Error de validación en backend (datos rechazados)")
    print("   2. ❌ Problema con CSRF token")
    print("   3. ❌ Error en JavaScript (formulario no se envía)")
    print("   4. ❌ Excepción no capturada en la vista")
    print("   5. ❌ Problema de permisos de usuario")
    
    print(f"\n   💡 SOLUCIONES RECOMENDADAS:")
    print("   1. ✅ Verificar logs del servidor Django")
    print("   2. ✅ Agregar logging detallado en la vista")
    print("   3. ✅ Verificar Network tab del navegador")
    print("   4. ✅ Probar sin validaciones JavaScript")
    
    return True

if __name__ == "__main__":
    investigar_problema_formulario()