#!/usr/bin/env python3
"""
Investigar qué pasó con LABUBU 3
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    ContenidoAnalitico, Asignatura, AuditoriaCreacionPractica,
    Titulo, Competencias, ObjetivoPractica
)
from datetime import datetime, timedelta

def investigar_labubu3():
    """Investigar qué pasó con LABUBU 3"""
    
    print("🔍 INVESTIGANDO LABUBU 3")
    print("=" * 50)
    
    # 1. Buscar por nombre en ContenidoAnalitico
    print("\n1. 📝 BÚSQUEDA POR NOMBRE EN CONTENIDOS:")
    busquedas = ['LABUBU 3', 'labubu 3', 'LABUBU', 'labubu', '3']
    
    for busqueda in busquedas:
        contenidos = ContenidoAnalitico.objects.filter(
            nombre__icontains=busqueda
        ).order_by('-created_at')
        
        if contenidos.exists():
            print(f"   📌 Contenidos con '{busqueda}':")
            for contenido in contenidos[:3]:  # Solo los primeros 3
                asig = contenido.unidad_didactica.asignatura
                print(f"      - '{contenido.nombre}' → {asig.get_nombre_display()} (ID: {asig.id}) - {contenido.created_at}")
    
    # 2. Buscar en Títulos
    print("\n2. 🏷️ BÚSQUEDA EN TÍTULOS:")
    for busqueda in ['LABUBU 3', 'labubu 3', 'LABUBU']:
        titulos = Titulo.objects.filter(
            texto__icontains=busqueda
        ).select_related('contenido_analitico__unidad_didactica__asignatura').order_by('-created_at')
        
        if titulos.exists():
            print(f"   📌 Títulos con '{busqueda}':")
            for titulo in titulos[:3]:
                contenido = titulo.contenido_analitico
                asig = contenido.unidad_didactica.asignatura
                print(f"      - Título: '{titulo.texto}' → Contenido: '{contenido.nombre}' → {asig.get_nombre_display()} (ID: {asig.id})")
    
    # 3. Verificar auditorías recientes
    print("\n3. 📋 AUDITORÍAS RECIENTES:")
    # Buscar auditorías de los últimos 30 minutos
    hace_30_min = datetime.now() - timedelta(minutes=30)
    auditorias_recientes = AuditoriaCreacionPractica.objects.filter(
        created_at__gte=hace_30_min
    ).order_by('-created_at')
    
    if auditorias_recientes.exists():
        print(f"   📊 Últimas {auditorias_recientes.count()} auditorías (últimos 30 min):")
        for auditoria in auditorias_recientes:
            print(f"      - '{auditoria.practica_nombre}' → {auditoria.asignatura_nombre} (ID: {auditoria.asignatura_id_usado})")
            print(f"        Usuario: {auditoria.usuario} - {auditoria.created_at}")
    else:
        print("   ❌ No hay auditorías recientes")
    
    # 4. Verificar últimos contenidos creados (últimos 10)
    print("\n4. 🕒 ÚLTIMOS CONTENIDOS CREADOS:")
    ultimos_contenidos = ContenidoAnalitico.objects.order_by('-created_at')[:10]
    
    for i, contenido in enumerate(ultimos_contenidos, 1):
        asig = contenido.unidad_didactica.asignatura
        tiempo_diff = datetime.now() - contenido.created_at.replace(tzinfo=None)
        minutos = int(tiempo_diff.total_seconds() / 60)
        
        print(f"   {i:2d}. '{contenido.nombre}' → {asig.get_nombre_display()} (ID: {asig.id}) - hace {minutos} min")
    
    # 5. Verificar específicamente FISICA II
    print("\n5. 🔬 VERIFICACIÓN EN FISICA II:")
    try:
        fisica_ii = Asignatura.objects.get(nombre='FISICA II')
        contenidos_fisica_ii = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=fisica_ii
        ).order_by('-created_at')[:5]
        
        print(f"   📚 FISICA II (ID: {fisica_ii.id}) - Últimos 5 contenidos:")
        for contenido in contenidos_fisica_ii:
            tiempo_diff = datetime.now() - contenido.created_at.replace(tzinfo=None)
            minutos = int(tiempo_diff.total_seconds() / 60)
            print(f"      - '{contenido.nombre}' - hace {minutos} min")
            
        print(f"   📊 Total contenidos en FISICA II: {ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=fisica_ii).count()}")
            
    except Asignatura.DoesNotExist:
        print("   ❌ No se encontró asignatura FISICA II")
    
    # 6. Verificar si hay errores en el proceso
    print("\n6. 🚨 DIAGNÓSTICO DE PROBLEMAS POTENCIALES:")
    
    # Verificar asignaturas problemáticas
    asignaturas_numericas = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    if asignaturas_numericas.exists():
        print("   ⚠️ Asignaturas problemáticas detectadas:")
        for asig in asignaturas_numericas:
            print(f"      - ID {asig.id}: '{asig.nombre}'")
        print("   💡 Estas podrían estar causando confusión en el formulario")
    
    # Verificar si hay múltiples asignaturas FISICA II
    fisica_ii_multiples = Asignatura.objects.filter(nombre__icontains='FISICA II')
    if fisica_ii_multiples.count() > 1:
        print("   ⚠️ Múltiples asignaturas con 'FISICA II':")
        for asig in fisica_ii_multiples:
            print(f"      - ID {asig.id}: '{asig.nombre}'")
    
    # 7. Recomendaciones
    print("\n7. 💡 POSIBLES CAUSAS Y SOLUCIONES:")
    print("   🔍 Causa 1: Error de validación - la práctica fue rechazada por el backend")
    print("   🔍 Causa 2: Se guardó en asignatura diferente de la esperada") 
    print("   🔍 Causa 3: Error en JavaScript - el formulario no se envió")
    print("   🔍 Causa 4: Error de red - la petición no llegó al servidor")
    
    print(f"\n   🎯 SIGUIENTE PASO:")
    print(f"      1. Verificar logs del servidor Django")
    print(f"      2. Revisar Network tab del navegador")
    print(f"      3. Probar nuevamente con logging detallado")
    
    return True

if __name__ == "__main__":
    investigar_labubu3()