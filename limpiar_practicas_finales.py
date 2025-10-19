#!/usr/bin/env python3
"""
Limpiar prácticas restantes en asignaturas problemáticas
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    ContenidoAnalitico, Asignatura, UnidadDidactica,
    MaterialesHerramientasEquipos, Titulo, Competencias, ObjetivoPractica
)

def limpiar_practicas_problematicas():
    """Migrar cualquier práctica restante de asignaturas problemáticas"""
    
    print("🧹 LIMPIEZA DE PRÁCTICAS EN ASIGNATURAS PROBLEMÁTICAS")
    print("=" * 60)
    
    # 1. Identificar asignaturas problemáticas con prácticas
    print("\n1. 🔍 IDENTIFICANDO ASIGNATURAS PROBLEMÁTICAS CON PRÁCTICAS:")
    asignaturas_problematicas = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    
    practicas_a_migrar = []
    
    for asig in asignaturas_problematicas:
        contenidos = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig)
        if contenidos.exists():
            print(f"   ⚠️ {asig.nombre} (ID: {asig.id}) → {contenidos.count()} prácticas")
            for contenido in contenidos:
                practicas_a_migrar.append({
                    'contenido': contenido,
                    'asignatura_problematica': asig,
                    'nombre_contenido': contenido.nombre
                })
    
    if not practicas_a_migrar:
        print("   ✅ No hay prácticas en asignaturas problemáticas")
        return True
    
    # 2. Migrar cada práctica a su asignatura correcta
    print(f"\n2. 🔄 MIGRANDO {len(practicas_a_migrar)} PRÁCTICAS:")
    
    # Mapeo de IDs problemáticos a asignaturas correctas
    mapeo_asignaturas = {
        '168': 'FISICA I',
        '169': 'QUIMICA GENERAL', 
        '170': 'FISICA II',
        '171': 'FISICOQUIMICA',
        '172': 'FISICA I',  # Asumir FISICA I por defecto
        '173': 'FISICA II', # Asumir FISICA II por defecto
        '174': 'QUIMICA GENERAL', # Asumir QUÍMICA por defecto
        '175': 'FISICOQUIMICA'
    }
    
    for practica_info in practicas_a_migrar:
        contenido = practica_info['contenido']
        asig_problematica = practica_info['asignatura_problematica']
        
        # Determinar asignatura correcta
        nombre_correcto = mapeo_asignaturas.get(asig_problematica.nombre)
        
        if nombre_correcto:
            try:
                asignatura_correcta = Asignatura.objects.get(nombre=nombre_correcto)
                
                # Buscar o crear unidad didáctica en la asignatura correcta
                unidades_correctas = UnidadDidactica.objects.filter(asignatura=asignatura_correcta)
                
                if unidades_correctas.exists():
                    unidad_destino = unidades_correctas.first()
                else:
                    # Crear unidad didáctica si no existe
                    unidad_destino = UnidadDidactica.objects.create(
                        asignatura=asignatura_correcta,
                        nombre=contenido.unidad_didactica.nombre,
                        descripcion='Migrado automáticamente desde asignatura problemática'
                    )
                
                # Contar recursos antes
                recursos_count = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).count()
                titulos_count = Titulo.objects.filter(contenido_analitico=contenido).count()
                competencias_count = Competencias.objects.filter(contenido_analitico=contenido).count()
                objetivos_count = ObjetivoPractica.objects.filter(contenido_analitico=contenido).count()
                
                print(f"\n   🔄 Migrando: '{contenido.nombre}'")
                print(f"      📤 Desde: {asig_problematica.nombre} (ID: {asig_problematica.id})")  
                print(f"      📥 Hacia: {nombre_correcto} (ID: {asignatura_correcta.id})")
                print(f"      📊 Recursos: {recursos_count} recursos, {titulos_count} títulos, {competencias_count} competencias, {objetivos_count} objetivos")
                
                # Realizar migración
                contenido.unidad_didactica = unidad_destino
                contenido.save()
                
                print(f"      ✅ Migración completada")
                
            except Asignatura.DoesNotExist:
                print(f"   ❌ No se encontró asignatura '{nombre_correcto}' para migrar desde '{asig_problematica.nombre}'")
                
        else:
            print(f"   ❓ No hay mapeo para asignatura problemática '{asig_problematica.nombre}' (ID: {asig_problematica.id})")
            print(f"      Práctica: '{contenido.nombre}'")
    
    # 3. Verificación final
    print(f"\n3. ✅ VERIFICACIÓN FINAL:")
    
    # Verificar que no queden prácticas en asignaturas problemáticas
    asignaturas_problematicas_restantes = []
    for asig in asignaturas_problematicas:
        contenidos_restantes = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
        if contenidos_restantes > 0:
            asignaturas_problematicas_restantes.append((asig, contenidos_restantes))
    
    if asignaturas_problematicas_restantes:
        print("   ⚠️ Asignaturas problemáticas con prácticas restantes:")
        for asig, count in asignaturas_problematicas_restantes:
            print(f"      - {asig.nombre} (ID: {asig.id}) → {count} prácticas")
    else:
        print("   🎉 ¡Todas las prácticas han sido migradas exitosamente!")
        
    # Estado final de asignaturas buenas
    print(f"\n   📊 Estado final de asignaturas legítimas:")
    asignaturas_buenas = ['FISICA I', 'QUIMICA GENERAL', 'FISICA II', 'FISICOQUIMICA']
    
    for nombre in asignaturas_buenas:
        try:
            asig = Asignatura.objects.get(nombre=nombre)
            count = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
            print(f"      ✅ {nombre} (ID: {asig.id}) → {count} prácticas")
        except Asignatura.DoesNotExist:
            print(f"      ❌ {nombre} → No encontrada")
    
    return True

if __name__ == "__main__":
    limpiar_practicas_problematicas()