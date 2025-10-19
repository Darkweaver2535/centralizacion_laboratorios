#!/usr/bin/env python3
"""
Buscar la práctica "labubu 2" recién creada
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

def buscar_labubu2():
    """Buscar dónde se guardó la práctica labubu 2"""
    
    print("🔍 BUSCANDO PRÁCTICA 'LABUBU 2'")
    print("=" * 50)
    
    # 1. Buscar en ContenidoAnalitico
    print("\n1. 📝 BÚSQUEDA EN CONTENIDOS ANALÍTICOS:")
    contenidos_labubu2 = ContenidoAnalitico.objects.filter(
        nombre__icontains='labubu 2'
    ).select_related('unidad_didactica__asignatura')
    
    if contenidos_labubu2.exists():
        for contenido in contenidos_labubu2:
            asig = contenido.unidad_didactica.asignatura
            print(f"   ✅ ENCONTRADO: '{contenido.nombre}'")
            print(f"      📚 Asignatura: {asig.get_nombre_display()} (ID: {asig.id})")
            print(f"      🔗 URL: http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/{asig.id}/")
            print(f"      📅 Creado: {contenido.created_at}")
    else:
        print("   ❌ No encontrado en ContenidoAnalitico")
    
    # 2. Buscar variaciones del nombre
    print("\n2. 🔍 BÚSQUEDA DE VARIACIONES:")
    variaciones = ['labubu', 'LABUBU', 'Labubu', '2']
    
    for variacion in variaciones:
        contenidos = ContenidoAnalitico.objects.filter(
            nombre__icontains=variacion
        ).order_by('-created_at')[:5]  # Últimos 5
        
        if contenidos.exists():
            print(f"   📌 Contenidos con '{variacion}':")
            for contenido in contenidos:
                asig = contenido.unidad_didactica.asignatura
                print(f"      - '{contenido.nombre}' → {asig.get_nombre_display()} (ID: {asig.id}) - {contenido.created_at}")
    
    # 3. Buscar en Títulos (por si se guardó ahí)
    print("\n3. 🏷️ BÚSQUEDA EN TÍTULOS:")
    titulos_labubu2 = Titulo.objects.filter(
        texto__icontains='labubu 2'
    ).select_related('contenido_analitico__unidad_didactica__asignatura')
    
    if titulos_labubu2.exists():
        for titulo in titulos_labubu2:
            contenido = titulo.contenido_analitico
            asig = contenido.unidad_didactica.asignatura
            print(f"   ✅ TÍTULO ENCONTRADO: '{titulo.texto}'")
            print(f"      📝 En contenido: '{contenido.nombre}'")
            print(f"      📚 Asignatura: {asig.get_nombre_display()} (ID: {asig.id})")
    else:
        print("   ❌ No encontrado en Títulos")
    
    # 4. Verificar registros de auditoría
    print("\n4. 📋 REGISTRO DE AUDITORÍA:")
    auditorias_recientes = AuditoriaCreacionPractica.objects.order_by('-created_at')[:10]
    
    if auditorias_recientes.exists():
        print("   📊 Últimas 10 creaciones registradas:")
        for auditoria in auditorias_recientes:
            print(f"      - '{auditoria.practica_nombre}' → {auditoria.asignatura_nombre} (ID: {auditoria.asignatura_id_usado}) - {auditoria.created_at}")
    else:
        print("   ❌ No hay registros de auditoría")
    
    # 5. Verificar últimos ContenidoAnalitico creados
    print("\n5. 🕒 ÚLTIMOS CONTENIDOS CREADOS:")
    ultimos_contenidos = ContenidoAnalitico.objects.order_by('-created_at')[:10]
    
    for contenido in ultimos_contenidos:
        asig = contenido.unidad_didactica.asignatura
        print(f"   - '{contenido.nombre}' → {asig.get_nombre_display()} (ID: {asig.id}) - {contenido.created_at}")
    
    # 6. Verificar específicamente FISICA I
    print("\n6. 🔬 VERIFICACIÓN EN FISICA I:")
    try:
        fisica_i = Asignatura.objects.get(nombre='FISICA I')
        contenidos_fisica_i = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=fisica_i
        ).order_by('-created_at')[:5]
        
        print(f"   📚 FISICA I (ID: {fisica_i.id}) - Últimos 5 contenidos:")
        for contenido in contenidos_fisica_i:
            print(f"      - '{contenido.nombre}' - {contenido.created_at}")
    except Asignatura.DoesNotExist:
        print("   ❌ No se encontró asignatura FISICA I")
    
    return True

if __name__ == "__main__":
    buscar_labubu2()