#!/usr/bin/env python3
"""
Simular exactamente lo que hace la vista detalle_asignatura_view
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    ContenidoAnalitico, Asignatura, MaterialesHerramientasEquipos,
    Titulo, Competencias, ObjetivoPractica
)

def simular_vista_fisica2():
    """Simular exactamente lo que hace la vista para FISICA II"""
    
    print("🔍 SIMULANDO VISTA DETALLE_ASIGNATURA_VIEW PARA FISICA II")
    print("=" * 60)
    
    # Obtener asignatura FISICA II (ID: 170)
    asignatura_id = 170
    
    try:
        asignatura = Asignatura.objects.get(id=asignatura_id)
        print(f"✅ Asignatura: {asignatura.nombre} (ID: {asignatura.id})")
    except Asignatura.DoesNotExist:
        print(f"❌ Asignatura ID {asignatura_id} no encontrada")
        return False
    
    # Simular la consulta exacta de la vista
    print(f"\n📋 CONSULTANDO CONTENIDOS ANALÍTICOS:")
    contenidos_analiticos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    ).select_related('unidad_didactica').order_by('-created_at')  # Más recientes primero
    
    print(f"   📊 Total contenidos encontrados: {contenidos_analiticos.count()}")
    
    # Mostrar los primeros 10
    print(f"\n📌 PRIMEROS 10 CONTENIDOS (como aparecerán en la vista):")
    
    combinaciones = []
    for indice, contenido in enumerate(contenidos_analiticos[:10], 1):
        # Simular la creación de combinación
        combinacion = {
            'id': contenido.id,
            'numero_combinacion': indice,
            'contenido_analitico': contenido,
            'unidad_didactica': contenido.unidad_didactica,
        }
        
        # Obtener componentes como en la vista real
        titulos = Titulo.objects.filter(contenido_analitico=contenido).order_by('orden')
        competencias = Competencias.objects.filter(contenido_analitico=contenido).order_by('orden')
        objetivos = ObjetivoPractica.objects.filter(contenido_analitico=contenido)
        
        titulo_texto = titulos.first().texto if titulos.exists() else contenido.nombre
        
        print(f"   {indice:2d}. Combinación #{indice}")
        print(f"       📝 ID: {contenido.id}")
        print(f"       📄 Nombre: '{contenido.nombre}'")
        print(f"       🏷️ Título: '{titulo_texto}'")
        print(f"       📚 Unidad: {contenido.unidad_didactica.nombre}")
        print(f"       📅 Creado: {contenido.created_at}")
        print(f"       📊 Componentes: {titulos.count()} títulos, {competencias.count()} competencias, {objetivos.count()} objetivos")
        
        # Verificar si es LABUBU 3
        if 'LABUBU 3' in contenido.nombre.upper() or (titulos.exists() and 'LABUBU 3' in titulos.first().texto.upper()):
            print(f"       🎯 ¡ESTE ES LABUBU 3!")
        
        print()
        
        combinaciones.append(combinacion)
    
    # Verificar específicamente LABUBU 3
    print(f"\n🎯 VERIFICACIÓN ESPECÍFICA DE LABUBU 3:")
    labubu3_contenido = contenidos_analiticos.filter(nombre__icontains='LABUBU 3').first()
    
    if labubu3_contenido:
        posicion = list(contenidos_analiticos).index(labubu3_contenido) + 1
        print(f"   ✅ LABUBU 3 encontrado en posición {posicion}")
        print(f"   📝 Nombre: '{labubu3_contenido.nombre}'")
        print(f"   📅 Creado: {labubu3_contenido.created_at}")
        
        if posicion <= 10:
            print(f"   🎉 ¡DEBERÍA APARECER en la primera página!")
        else:
            print(f"   ⚠️ Está en posición {posicion}, podría estar paginado")
    else:
        print(f"   ❌ LABUBU 3 no encontrado en la consulta")
    
    # Verificar URL que se generaría
    print(f"\n🔗 URL DE LA VISTA:")
    print(f"   http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/{asignatura.id}/")
    
    return True

if __name__ == "__main__":
    simular_vista_fisica2()