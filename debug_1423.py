#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== VERIFICACIÓN DETALLADA DEL CONTENIDO 1423 ===")

try:
    # Buscar el contenido específico
    contenido = ContenidoAnalitico.objects.get(id=1423)
    print(f"Contenido encontrado: {contenido.nombre}")
    print(f"Unidad didáctica: {contenido.unidad_didactica.nombre}")
    print(f"Asignatura: {contenido.unidad_didactica.asignatura.get_nombre_display()}")
    print(f"ID de asignatura: {contenido.unidad_didactica.asignatura.id}")
    
    # Verificar títulos asociados
    titulos = Titulo.objects.filter(contenido_analitico=contenido)
    print(f"\nTítulos asociados: {titulos.count()}")
    for titulo in titulos:
        print(f"  - {titulo.texto}")
    
    # Verificar recursos asociados
    recursos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido)
    print(f"\nRecursos asociados: {recursos.count()}")
    
    # Verificar competencias
    competencias = Competencias.objects.filter(contenido_analitico=contenido)
    print(f"Competencias: {competencias.count()}")
    
    # Verificar objetivos
    objetivos = ObjetivoPractica.objects.filter(contenido_analitico=contenido)
    print(f"Objetivos: {objetivos.count()}")
    
    print(f"\n=== QUERY SIMULANDO LA VISTA ===")
    
    # Simular exactamente lo que hace la vista
    asignatura = contenido.unidad_didactica.asignatura
    contenidos_vista = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    ).select_related('unidad_didactica').order_by('unidad_didactica__nombre', 'nombre')
    
    print(f"Total contenidos en vista: {contenidos_vista.count()}")
    
    # Buscar nuestro contenido en la lista
    encontrado = False
    for i, c in enumerate(contenidos_vista):
        if c.id == 1423:
            print(f"¡Encontrado en posición {i+1}!")
            print(f"Contenido: {c.nombre}")
            encontrado = True
            break
    
    if not encontrado:
        print("❌ NO ENCONTRADO en la query de la vista")
        
        # Verificar por qué no aparece
        print("\n=== DEBUGGING ===")
        print(f"Unidad didáctica del contenido: {contenido.unidad_didactica}")
        print(f"Asignatura de la unidad: {contenido.unidad_didactica.asignatura}")
        
        # Verificar si la unidad didáctica existe y está bien asociada
        unidades = UnidadDidactica.objects.filter(asignatura=asignatura)
        print(f"Unidades didácticas de la asignatura: {unidades.count()}")
        for u in unidades:
            contenidos_u = ContenidoAnalitico.objects.filter(unidad_didactica=u)
            print(f"  - {u.nombre}: {contenidos_u.count()} contenidos")
            if u.id == contenido.unidad_didactica.id:
                print(f"    -> Nuestra unidad didáctica")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN VERIFICACIÓN ===")