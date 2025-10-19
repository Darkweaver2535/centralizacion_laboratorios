#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== VERIFICACIÓN QUIMICA GENERAL (ID 169) ===")

try:
    asignatura = Asignatura.objects.get(id=169)
    print(f"Asignatura: {asignatura.get_nombre_display()}")
    
    # Verificar contenidos analíticos
    contenidos = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=asignatura
    ).order_by('-id')  # Los más recientes primero
    
    print(f"Total contenidos analíticos: {contenidos.count()}")
    
    # Buscar el título "PRUEBA LABUBU"
    print("\n=== BÚSQUEDA DE 'PRUEBA LABUBU' ===")
    
    # Buscar en títulos
    titulos_labubu = Titulo.objects.filter(texto__icontains='LABUBU')
    print(f"Títulos con 'LABUBU': {titulos_labubu.count()}")
    
    for titulo in titulos_labubu:
        print(f"  - Título: {titulo.texto}")
        print(f"  - Contenido: {titulo.contenido_analitico.nombre}")
        print(f"  - Asignatura: {titulo.contenido_analitico.unidad_didactica.asignatura.get_nombre_display()}")
        print(f"  - ID Contenido: {titulo.contenido_analitico.id}")
        print("---")
    
    # Buscar en contenidos analíticos
    contenidos_labubu = ContenidoAnalitico.objects.filter(nombre__icontains='LABUBU')
    print(f"Contenidos con 'LABUBU': {contenidos_labubu.count()}")
    
    for contenido in contenidos_labubu:
        print(f"  - Contenido: {contenido.nombre}")
        print(f"  - Asignatura: {contenido.unidad_didactica.asignatura.get_nombre_display()}")
        print(f"  - ID: {contenido.id}")
        print("---")
    
    # Mostrar los últimos 5 contenidos de QUÍMICA GENERAL
    print(f"\n=== ÚLTIMOS 5 CONTENIDOS DE QUÍMICA GENERAL ===")
    ultimos_contenidos = contenidos[:5]
    
    for contenido in ultimos_contenidos:
        print(f"ID: {contenido.id} - {contenido.nombre}")
        
        # Verificar si tiene títulos específicos
        titulos = Titulo.objects.filter(contenido_analitico=contenido)
        if titulos:
            print(f"  -> Títulos: {[t.texto for t in titulos]}")
        else:
            print(f"  -> Sin títulos específicos")
        print("---")
            
except Exception as e:
    print(f"Error: {e}")

print("\n=== FIN VERIFICACIÓN ===")