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

print("=== MIGRACIÓN DE DATOS DE ASIGNATURAS ===")

# Mapeo de asignaturas problemáticas a correctas
migraciones = [
    (176, 169),  # De '169' (ID 176) a QUIMICA GENERAL (ID 169)
    (175, 171),  # De '171' (ID 175) a FISICOQUIMICA (ID 171)
]

try:
    with transaction.atomic():
        
        for id_origen, id_destino in migraciones:
            print(f"\n--- Migrando de ID {id_origen} a ID {id_destino} ---")
            
            # Obtener asignaturas
            asig_origen = Asignatura.objects.get(id=id_origen)
            asig_destino = Asignatura.objects.get(id=id_destino)
            
            print(f"Origen: '{asig_origen.nombre}' (ID {asig_origen.id})")
            print(f"Destino: '{asig_destino.get_nombre_display()}' (ID {asig_destino.id})")
            
            # 1. Obtener o crear unidad didáctica en destino
            unidades_origen = UnidadDidactica.objects.filter(asignatura=asig_origen)
            
            for unidad_origen in unidades_origen:
                print(f"  Procesando unidad: {unidad_origen.nombre}")
                
                # Buscar o crear unidad didáctica equivalente en destino
                unidad_destino, created = UnidadDidactica.objects.get_or_create(
                    asignatura=asig_destino,
                    nombre=unidad_origen.nombre,
                    defaults={
                        'descripcion': unidad_origen.descripcion or unidad_origen.nombre
                    }
                )
                
                if created:
                    print(f"    ✅ Creada nueva unidad didáctica: {unidad_destino.nombre}")
                else:
                    print(f"    ♻️ Usando unidad didáctica existente: {unidad_destino.nombre}")
                
                # 2. Mover contenidos analíticos
                contenidos_origen = ContenidoAnalitico.objects.filter(unidad_didactica=unidad_origen)
                
                for contenido in contenidos_origen:
                    print(f"    Moviendo contenido: {contenido.nombre}")
                    
                    # Cambiar la unidad didáctica del contenido
                    contenido.unidad_didactica = unidad_destino
                    contenido.save()
                    
                    # Verificar recursos asociados
                    recursos = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido)
                    titulos = Titulo.objects.filter(contenido_analitico=contenido)
                    competencias = Competencias.objects.filter(contenido_analitico=contenido)
                    objetivos = ObjetivoPractica.objects.filter(contenido_analitico=contenido)
                    
                    print(f"      → {recursos.count()} recursos")
                    print(f"      → {titulos.count()} títulos")
                    print(f"      → {competencias.count()} competencias") 
                    print(f"      → {objetivos.count()} objetivos")
                    
                    # Mostrar títulos para identificación
                    for titulo in titulos:
                        print(f"      → Título: '{titulo.texto}'")
                
                # 3. Eliminar unidad didáctica origen (si está vacía)
                if not ContenidoAnalitico.objects.filter(unidad_didactica=unidad_origen).exists():
                    print(f"    🗑️ Eliminando unidad didáctica vacía: {unidad_origen.nombre}")
                    unidad_origen.delete()
        
        print(f"\n=== VERIFICACIÓN POST-MIGRACIÓN ===")
        
        # Verificar que PRUEBA LABUBU está ahora en QUIMICA GENERAL
        titulos_labubu = Titulo.objects.filter(texto__icontains='LABUBU')
        for titulo in titulos_labubu:
            contenido = titulo.contenido_analitico
            asig = contenido.unidad_didactica.asignatura
            print(f"PRUEBA LABUBU ahora está en:")
            print(f"  - Asignatura ID {asig.id}: '{asig.get_nombre_display()}'")
            print(f"  - Contenido ID {contenido.id}")
        
        # Verificar recursos en asignaturas correctas
        print(f"\nRecursos por asignatura después de migración:")
        for nombre, id_asig in [("QUIMICA GENERAL", 169), ("FISICOQUIMICA", 171)]:
            asig = Asignatura.objects.get(id=id_asig)
            recursos = MaterialesHerramientasEquipos.objects.filter(
                contenido_analitico__unidad_didactica__asignatura=asig
            ).count()
            contenidos = ContenidoAnalitico.objects.filter(
                unidad_didactica__asignatura=asig
            ).count()
            print(f"  - {nombre} (ID {id_asig}): {contenidos} contenidos, {recursos} recursos")
        
        print(f"\n✅ Migración completada exitosamente!")
        
        # Preguntar si eliminar asignaturas problemáticas
        print(f"\n=== LIMPIEZA OPCIONAL ===")
        print("Las asignaturas numéricas ahora están vacías y se pueden eliminar.")
        
except Exception as e:
    print(f"❌ Error durante la migración: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FIN MIGRACIÓN ===")