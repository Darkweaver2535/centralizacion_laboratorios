#!/usr/bin/env python3
"""
Verificar específicamente LABUBU 3 en FISICA II
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    ContenidoAnalitico, Asignatura, Titulo, Competencias, 
    ObjetivoPractica, AuditoriaCreacionPractica
)

def verificar_labubu3_fisica2():
    """Verificar específicamente LABUBU 3 en FISICA II"""
    
    print("🔍 VERIFICANDO LABUBU 3 EN FISICA II")
    print("=" * 50)
    
    # 1. Verificar FISICA II
    print("\n1. 📚 VERIFICANDO FISICA II:")
    try:
        fisica_ii = Asignatura.objects.get(id=170)
        print(f"   ✅ FISICA II encontrada: '{fisica_ii.nombre}' (ID: {fisica_ii.id})")
    except Asignatura.DoesNotExist:
        print("   ❌ FISICA II (ID: 170) no encontrada")
        return False
    
    # 2. Buscar LABUBU 3 específicamente
    print("\n2. 🔍 BUSCANDO LABUBU 3:")
    
    # Buscar por nombre exacto
    labubu3_exacto = ContenidoAnalitico.objects.filter(
        nombre__iexact='LABUBU 3',
        unidad_didactica__asignatura=fisica_ii
    )
    
    if labubu3_exacto.exists():
        contenido = labubu3_exacto.first()
        print(f"   ✅ LABUBU 3 encontrado: ID {contenido.id}")
        print(f"      📅 Creado: {contenido.created_at}")
        print(f"      📚 Unidad: {contenido.unidad_didactica.nombre}")
    else:
        print("   ❌ 'LABUBU 3' NO encontrado con nombre exacto")
    
    # Buscar variaciones
    variaciones = ['LABUBU 3', 'labubu 3', 'Labubu 3', 'LABUBU3', 'labubu3']
    
    for variacion in variaciones:
        contenidos = ContenidoAnalitico.objects.filter(
            nombre__icontains=variacion,
            unidad_didactica__asignatura=fisica_ii
        )
        
        if contenidos.exists():
            print(f"   📌 Variación '{variacion}' encontrada:")
            for contenido in contenidos:
                print(f"      - ID {contenido.id}: '{contenido.nombre}' - {contenido.created_at}")
    
    # 3. Verificar todos los contenidos de FISICA II
    print(f"\n3. 📋 TODOS LOS CONTENIDOS EN FISICA II:")
    contenidos_fisica_ii = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=fisica_ii
    ).order_by('-created_at')[:10]  # Últimos 10
    
    print(f"   📊 Total contenidos en FISICA II: {ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=fisica_ii).count()}")
    print(f"   📌 Últimos 10 contenidos:")
    
    for i, contenido in enumerate(contenidos_fisica_ii, 1):
        print(f"   {i:2d}. ID {contenido.id}: '{contenido.nombre}' - {contenido.created_at}")
    
    # 4. Buscar en títulos
    print(f"\n4. 🏷️ BÚSQUEDA EN TÍTULOS:")
    titulos_labubu3 = Titulo.objects.filter(
        texto__icontains='LABUBU 3',
        contenido_analitico__unidad_didactica__asignatura=fisica_ii
    )
    
    if titulos_labubu3.exists():
        for titulo in titulos_labubu3:
            contenido = titulo.contenido_analitico
            print(f"   ✅ Título encontrado: '{titulo.texto}'")
            print(f"      📝 En contenido: '{contenido.nombre}' (ID: {contenido.id})")
    else:
        print("   ❌ No se encontró título 'LABUBU 3' en FISICA II")
    
    # 5. Verificar auditorías
    print(f"\n5. 📊 AUDITORÍAS DE LABUBU 3:")
    auditorias_labubu3 = AuditoriaCreacionPractica.objects.filter(
        practica_nombre__icontains='LABUBU 3'
    )
    
    if auditorias_labubu3.exists():
        for auditoria in auditorias_labubu3:
            print(f"   📋 Auditoría ID {auditoria.id}:")
            print(f"      📝 Práctica: '{auditoria.practica_nombre}'")
            print(f"      📚 Asignatura destino: {auditoria.asignatura_nombre} (ID: {auditoria.asignatura_id_usado})")
            print(f"      📅 Creado: {auditoria.created_at}")
            
            if auditoria.contenido_analitico:
                print(f"      🔗 ContenidoAnalítico: ID {auditoria.contenido_analitico.id}")
            else:
                print(f"      ⚠️ ContenidoAnalítico: No enlazado")
    else:
        print("   ❌ No hay auditorías de LABUBU 3")
    
    # 6. Búsqueda global de LABUBU 3
    print(f"\n6. 🌐 BÚSQUEDA GLOBAL DE LABUBU 3:")
    labubu3_global = ContenidoAnalitico.objects.filter(
        nombre__icontains='LABUBU 3'
    ).select_related('unidad_didactica__asignatura')
    
    if labubu3_global.exists():
        print(f"   📌 LABUBU 3 encontrado en otras asignaturas:")
        for contenido in labubu3_global:
            asig = contenido.unidad_didactica.asignatura
            print(f"      - '{contenido.nombre}' → {asig.nombre} (ID: {asig.id}) - {contenido.created_at}")
    else:
        print("   ❌ LABUBU 3 no encontrado en ninguna asignatura")
    
    # 7. Verificar últimos contenidos creados globalmente
    print(f"\n7. 🕒 ÚLTIMOS CONTENIDOS CREADOS (GLOBAL):")
    ultimos_contenidos = ContenidoAnalitico.objects.order_by('-created_at')[:5]
    
    for i, contenido in enumerate(ultimos_contenidos, 1):
        asig = contenido.unidad_didactica.asignatura
        print(f"   {i}. '{contenido.nombre}' → {asig.nombre} (ID: {asig.id}) - {contenido.created_at}")
    
    return True

if __name__ == "__main__":
    verificar_labubu3_fisica2()