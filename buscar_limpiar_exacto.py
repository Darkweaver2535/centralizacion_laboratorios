#!/usr/bin/env python
"""
Script para buscar específicamente las pruebas que hicimos y limpiarlas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def buscar_pruebas_exactas():
    print("🔍 BUSCANDO PRUEBAS EXACTAS QUE CREAMOS")
    print("=" * 60)
    
    # Buscar por nombres exactos que usamos
    nombres_exactos = [
        'PRUEBA 00', 'FINAL', 'FUNCIONA FINAL', 'LABUBU', 'LABUBU 2', 'LABUBU 3', 
        'LABUBU 4', 'LABUBU 5', 'PRUEBA 90'
    ]
    
    total_encontrados = 0
    
    # Buscar en ContenidoAnalitico
    print(f"\n📊 CONTENIDOS ANALÍTICOS:")
    for nombre in nombres_exactos:
        contenidos = ContenidoAnalitico.objects.filter(nombre__iexact=nombre)
        if contenidos.exists():
            for contenido in contenidos:
                asignatura = contenido.unidad_didactica.asignatura
                print(f"   🧪 '{contenido.nombre}' (ID: {contenido.id}) en {asignatura.nombre}")
                total_encontrados += 1
    
    # Buscar en Títulos
    print(f"\n📝 TÍTULOS:")
    for nombre in nombres_exactos:
        titulos = Titulo.objects.filter(texto__iexact=nombre)
        if titulos.exists():
            for titulo in titulos:
                asignatura = titulo.contenido_analitico.unidad_didactica.asignatura
                print(f"   📝 '{titulo.texto}' en contenido: {titulo.contenido_analitico.nombre} - {asignatura.nombre}")
                total_encontrados += 1
    
    # Buscar en auditorías
    print(f"\n📋 AUDITORÍAS:")
    auditorias = AuditoriaCreacionPractica.objects.all().order_by('-created_at')[:10]
    for auditoria in auditorias:
        print(f"   📋 ID: {auditoria.id} - '{auditoria.practica_nombre}' en {auditoria.asignatura_nombre}")
        print(f"      Fecha: {auditoria.created_at}")
    
    # Buscar las últimas creaciones
    print(f"\n🕒 ÚLTIMOS CONTENIDOS CREADOS:")
    ultimos_contenidos = ContenidoAnalitico.objects.all().order_by('-id')[:10]
    for contenido in ultimos_contenidos:
        asignatura = contenido.unidad_didactica.asignatura
        print(f"   🧪 ID: {contenido.id} - '{contenido.nombre}' en {asignatura.nombre}")
    
    print(f"\n📊 Total elementos de prueba encontrados: {total_encontrados}")

def limpiar_por_ids():
    print(f"\n🧹 LIMPIEZA POR IDs ESPECÍFICOS")
    print("=" * 40)
    
    # IDs que vimos en los logs
    ids_sospechosos = [1415, 1420, 1257, 1426]  # IDs que aparecieron en los logs
    
    eliminados = 0
    
    for contenido_id in ids_sospechosos:
        try:
            contenido = ContenidoAnalitico.objects.get(id=contenido_id)
            
            # Verificar si tiene datos de prueba
            tiene_pruebas = False
            
            # Verificar títulos
            titulos = Titulo.objects.filter(contenido_analitico=contenido)
            for titulo in titulos:
                if any(palabra in titulo.texto.upper() for palabra in ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA']):
                    tiene_pruebas = True
                    print(f"   🗑️ Eliminando contenido ID {contenido_id}: '{contenido.nombre}' (tiene título de prueba: '{titulo.texto}')")
                    break
            
            # Verificar si el nombre mismo es de prueba
            if any(palabra in contenido.nombre.upper() for palabra in ['PRUEBA', 'LABUBU', 'FINAL', 'FUNCIONA']):
                tiene_pruebas = True
                print(f"   🗑️ Eliminando contenido ID {contenido_id}: '{contenido.nombre}' (nombre de prueba)")
            
            if tiene_pruebas:
                # Eliminar todo lo relacionado
                Titulo.objects.filter(contenido_analitico=contenido).delete()
                Bibliografia.objects.filter(contenido_analitico=contenido).delete()
                PracticaLaboratorio.objects.filter(contenido_analitico=contenido).delete()
                Competencias.objects.filter(contenido_analitico=contenido).delete()
                ObjetivoPractica.objects.filter(contenido_analitico=contenido).delete()
                FundamentoTeorico.objects.filter(contenido_analitico=contenido).delete()
                MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).delete()
                Procedimientos.objects.filter(contenido_analitico=contenido).delete()
                CalculosResultados.objects.filter(contenido_analitico=contenido).delete()
                Cuestionario.objects.filter(contenido_analitico=contenido).delete()
                
                contenido.delete()
                eliminados += 1
        
        except ContenidoAnalitico.DoesNotExist:
            pass
    
    # Limpiar auditorías de las últimas 24 horas (nuestras pruebas)
    from datetime import datetime, timedelta
    hace_24h = datetime.now() - timedelta(hours=24)
    
    auditorias_recientes = AuditoriaCreacionPractica.objects.filter(
        created_at__gte=hace_24h
    )
    
    auditorias_eliminadas = auditorias_recientes.count()
    auditorias_recientes.delete()
    
    print(f"\n✅ Eliminados {eliminados} contenidos con datos de prueba")
    print(f"✅ Eliminadas {auditorias_eliminadas} auditorías de las últimas 24 horas")

if __name__ == "__main__":
    buscar_pruebas_exactas()
    
    respuesta = input("\n¿Proceder con la limpieza? (s/n): ")
    if respuesta.lower() == 's':
        limpiar_por_ids()
        print("\n🎉 Limpieza completada - Base de datos lista para pruebas profesionales")
    else:
        print("\n❌ Limpieza cancelada")