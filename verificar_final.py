#!/usr/bin/env python
"""
Script para verificar qué pasó con "FINAL" en FISICA I
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_final_fisica_i():
    print("🔍 VERIFICANDO 'FINAL' EN FISICA I")
    print("=" * 60)
    
    # Buscar FISICA I
    fisica_i = Asignatura.objects.filter(nombre__icontains='FISICA I').first()
    
    if fisica_i:
        print(f"📚 FISICA I encontrada: {fisica_i.nombre} (ID: {fisica_i.id})")
        
        # Buscar todas las referencias a "FINAL"
        print(f"\n🔍 Buscando 'FINAL' en FISICA I:")
        
        # En títulos
        titulos = Titulo.objects.filter(
            texto__icontains='FINAL',
            contenido_analitico__unidad_didactica__asignatura=fisica_i
        )
        print(f"   📝 Títulos con 'FINAL': {titulos.count()}")
        for titulo in titulos:
            print(f"      - '{titulo.texto}' en contenido: {titulo.contenido_analitico.nombre}")
        
        # En contenidos analíticos
        contenidos = ContenidoAnalitico.objects.filter(
            nombre__icontains='FINAL',
            unidad_didactica__asignatura=fisica_i
        )
        print(f"   🧪 Contenidos con 'FINAL': {contenidos.count()}")
        for contenido in contenidos:
            print(f"      - '{contenido.nombre}' (ID: {contenido.id})")
        
        # En prácticas de laboratorio
        practicas = PracticaLaboratorio.objects.filter(
            nombre__icontains='FINAL',
            contenido_analitico__unidad_didactica__asignatura=fisica_i
        )
        print(f"   🔬 Prácticas con 'FINAL': {practicas.count()}")
        for practica in practicas:
            print(f"      - '{practica.nombre}' en contenido: {practica.contenido_analitico.nombre}")
    
    # Buscar en toda la base de datos
    print(f"\n🔍 BUSCANDO 'FINAL' EN TODA LA BASE DE DATOS:")
    
    # Últimas auditorías
    auditorias = AuditoriaCreacionPractica.objects.filter(
        practica_nombre__icontains='FINAL'
    ).order_by('-created_at')[:3]
    
    print(f"   📋 Auditorías con 'FINAL': {auditorias.count()}")
    for auditoria in auditorias:
        print(f"      - '{auditoria.practica_nombre}' en {auditoria.asignatura_nombre} (ID: {auditoria.asignatura_id_usado})")
        print(f"        Fecha: {auditoria.created_at}")
    
    # Todos los títulos con FINAL
    todos_titulos = Titulo.objects.filter(texto__icontains='FINAL')
    print(f"\n   📝 Todos los títulos con 'FINAL': {todos_titulos.count()}")
    for titulo in todos_titulos:
        asignatura = titulo.contenido_analitico.unidad_didactica.asignatura
        print(f"      - '{titulo.texto}' en {asignatura.nombre} (contenido: {titulo.contenido_analitico.nombre})")

if __name__ == "__main__":
    verificar_final_fisica_i()