#!/usr/bin/env python
"""
Script para verificar qué se guardó realmente con "PRUEBA 00"
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def verificar_ultima_creacion():
    print("🔍 VERIFICANDO ÚLTIMA CREACIÓN CON 'PRUEBA 00'")
    print("=" * 60)
    
    # Buscar en auditoría la última creación
    ultima_auditoria = AuditoriaCreacionPractica.objects.order_by('-created_at').first()
    
    if ultima_auditoria:
        print(f"\n📋 ÚLTIMA AUDITORÍA (ID: {ultima_auditoria.id}):")
        print(f"   👤 Usuario: {ultima_auditoria.usuario}")
        print(f"   📅 Fecha: {ultima_auditoria.created_at}")
        print(f"   📚 Asignatura: {ultima_auditoria.asignatura_nombre} (ID: {ultima_auditoria.asignatura_id_usado})")
        print(f"   🧪 Práctica: {ultima_auditoria.practica_nombre}")
        print(f"   🔗 Contenido ID: {ultima_auditoria.contenido_analitico.id if ultima_auditoria.contenido_analitico else 'N/A'}")
    
    # Buscar contenidos analíticos recientes
    print(f"\n📊 CONTENIDOS ANALÍTICOS EN FISICOQUIMICA (ID 171):")
    asignatura = Asignatura.objects.get(id=171)
    
    for unidad in UnidadDidactica.objects.filter(asignatura=asignatura):
        print(f"\n   📖 Unidad: {unidad.nombre}")
        contenidos = ContenidoAnalitico.objects.filter(unidad_didactica=unidad).order_by('-id')[:5]
        
        for contenido in contenidos:
            print(f"      🧪 ID: {contenido.id} - {contenido.nombre}")
            
            # Verificar si tiene datos relacionados recientes
            titulos = Titulo.objects.filter(contenido_analitico=contenido)
            bibliografias = Bibliografia.objects.filter(contenido_analitico=contenido)
            
            if titulos.exists():
                print(f"         📝 Títulos: {[t.texto for t in titulos]}")
            if bibliografias.exists():
                print(f"         📚 Bibliografías: {[b.titulo for b in bibliografias]}")

def buscar_prueba_00():
    print(f"\n🔍 BUSCANDO 'PRUEBA 00' EN TODA LA BASE DE DATOS:")
    print("=" * 60)
    
    # Buscar en títulos
    titulos = Titulo.objects.filter(texto__icontains='PRUEBA 00')
    print(f"\n📝 En Títulos: {titulos.count()} resultados")
    for titulo in titulos:
        print(f"   - {titulo.texto} (Contenido ID: {titulo.contenido_analitico.id})")
    
    # Buscar en nombres de contenido analítico
    contenidos = ContenidoAnalitico.objects.filter(nombre__icontains='PRUEBA 00')
    print(f"\n🧪 En Contenidos Analíticos: {contenidos.count()} resultados")
    for contenido in contenidos:
        print(f"   - {contenido.nombre} (ID: {contenido.id})")
    
    # Buscar en bibliografías
    bibliografias = Bibliografia.objects.filter(titulo__icontains='PRUEBA 00')
    print(f"\n📚 En Bibliografías: {bibliografias.count()} resultados")
    for biblio in bibliografias:
        print(f"   - {biblio.titulo} (Contenido ID: {biblio.contenido_analitico.id})")
    
    # Buscar en prácticas de laboratorio
    practicas = PracticaLaboratorio.objects.filter(nombre__icontains='PRUEBA 00')
    print(f"\n🔬 En Prácticas de Laboratorio: {practicas.count()} resultados")
    for practica in practicas:
        print(f"   - {practica.nombre} (Contenido ID: {practica.contenido_analitico.id})")

if __name__ == "__main__":
    verificar_ultima_creacion()
    buscar_prueba_00()