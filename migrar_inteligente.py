#!/usr/bin/env python
import os
import sys
import django
from django.db import transaction

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

print("=== MIGRACIÓN INTELIGENTE DE DATOS ===")

try:
    with transaction.atomic():
        
        # Migrar de ID 176 ('169') a ID 169 (QUIMICA GENERAL)
        print("--- Migrando PRUEBA LABUBU a QUÍMICA GENERAL ---")
        
        asig_origen = Asignatura.objects.get(id=176)  # '169'
        asig_destino = Asignatura.objects.get(id=169)  # QUIMICA GENERAL
        
        print(f"Origen: '{asig_origen.nombre}' (ID {asig_origen.id})")
        print(f"Destino: '{asig_destino.get_nombre_display()}' (ID {asig_destino.id})")
        
        # Obtener la unidad didáctica problemática
        unidad_origen = UnidadDidactica.objects.get(asignatura=asig_origen, nombre='167')
        print(f"Unidad origen: {unidad_origen.nombre}")
        
        # Buscar una unidad didáctica apropiada en destino (usaremos la primera disponible)
        unidades_destino = UnidadDidactica.objects.filter(asignatura=asig_destino)
        if unidades_destino.exists():
            # Usar la primera unidad didáctica disponible
            unidad_destino = unidades_destino.first()
            print(f"Usando unidad existente en destino: {unidad_destino.nombre}")
        else:
            # Crear nueva unidad con nombre único
            nombre_unico = f"QUIMICA_PRACTICA_LABORATORIO_{asig_destino.id}"
            unidad_destino = UnidadDidactica.objects.create(
                asignatura=asig_destino,
                nombre=nombre_unico,
                descripcion="Prácticas de laboratorio de Química General"
            )
            print(f"Creada nueva unidad: {unidad_destino.nombre}")
        
        # Mover todos los contenidos analíticos
        contenidos_origen = ContenidoAnalitico.objects.filter(unidad_didactica=unidad_origen)
        
        for contenido in contenidos_origen:
            print(f"\nMoviendo contenido: {contenido.nombre} (ID {contenido.id})")
            
            # Verificar datos asociados ANTES del movimiento
            recursos_antes = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido)
            titulos_antes = Titulo.objects.filter(contenido_analitico=contenido)
            competencias_antes = Competencias.objects.filter(contenido_analitico=contenido)
            objetivos_antes = ObjetivoPractica.objects.filter(contenido_analitico=contenido)
            
            print(f"  Datos asociados:")
            print(f"    → {recursos_antes.count()} recursos")
            print(f"    → {titulos_antes.count()} títulos")
            print(f"    → {competencias_antes.count()} competencias")
            print(f"    → {objetivos_antes.count()} objetivos")
            
            # Mostrar títulos específicos
            for titulo in titulos_antes:
                print(f"    → Título: '{titulo.texto}'")
            
            # Cambiar la unidad didáctica (esto mantiene todas las relaciones FK)
            contenido.unidad_didactica = unidad_destino
            contenido.save()
            print(f"  ✅ Contenido movido exitosamente")
            
            # Verificar que los datos se mantuvieron después del movimiento
            recursos_despues = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido)
            titulos_despues = Titulo.objects.filter(contenido_analitico=contenido)
            
            print(f"  Verificación post-movimiento:")
            print(f"    → {recursos_despues.count()} recursos (mantenidos)")
            print(f"    → {titulos_despues.count()} títulos (mantenidos)")
        
        # Eliminar la unidad didáctica origen si quedó vacía
        if not ContenidoAnalitico.objects.filter(unidad_didactica=unidad_origen).exists():
            print(f"\n🗑️ Eliminando unidad didáctica vacía: {unidad_origen.nombre}")
            unidad_origen.delete()
        
        print(f"\n=== VERIFICACIÓN FINAL ===")
        
        # Verificar que PRUEBA LABUBU está ahora en QUÍMICA GENERAL
        titulos_labubu = Titulo.objects.filter(texto__icontains='LABUBU')
        for titulo in titulos_labubu:
            contenido = titulo.contenido_analitico
            asig = contenido.unidad_didactica.asignatura
            print(f"✅ PRUEBA LABUBU ahora está en:")
            print(f"   Asignatura: {asig.get_nombre_display()} (ID {asig.id})")
            print(f"   URL correcta: http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/{asig.id}/")
        
        # Verificar recursos totales en QUÍMICA GENERAL
        recursos_quimica = MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico__unidad_didactica__asignatura_id=169
        ).count()
        
        contenidos_quimica = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura_id=169
        ).count()
        
        print(f"\n📊 QUÍMICA GENERAL ahora tiene:")
        print(f"   - {contenidos_quimica} contenidos analíticos")
        print(f"   - {recursos_quimica} recursos totales")
        
        print(f"\n🎉 ¡Migración completada exitosamente!")
        print(f"Ahora 'PRUEBA LABUBU' debe aparecer en:")
        print(f"http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/169/")
        
except Exception as e:
    print(f"❌ Error durante la migración: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN MIGRACIÓN ===")