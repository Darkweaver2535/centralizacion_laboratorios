#!/usr/bin/env python3
"""
Buscar y migrar la práctica recién creada al lugar correcto
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    ContenidoAnalitico, Asignatura, AuditoriaCreacionPractica,
    Titulo, Competencias, ObjetivoPractica, UnidadDidactica,
    MaterialesHerramientasEquipos
)

def migrar_practica_correcta():
    """Encontrar y migrar la práctica al lugar correcto"""
    
    print("🔧 MIGRANDO PRÁCTICA RECIÉN CREADA")
    print("=" * 50)
    
    # 1. Buscar la auditoría más reciente
    print("\n1. 📋 BUSCANDO ÚLTIMA AUDITORÍA:")
    auditoria_reciente = AuditoriaCreacionPractica.objects.order_by('-created_at').first()
    
    if auditoria_reciente:
        print(f"   ✅ Auditoría encontrada: ID {auditoria_reciente.id}")
        print(f"   📝 Práctica: '{auditoria_reciente.practica_nombre}'")
        print(f"   📚 Se guardó en: {auditoria_reciente.asignatura_nombre} (ID: {auditoria_reciente.asignatura_id_usado})")
        print(f"   👤 Usuario: {auditoria_reciente.usuario}")
        print(f"   🕒 Fecha: {auditoria_reciente.created_at}")
        
        # Buscar el contenido analítico correspondiente
        contenido_id = auditoria_reciente.contenido_analitico.id if auditoria_reciente.contenido_analitico else None
        
        if contenido_id:
            contenido = ContenidoAnalitico.objects.get(id=contenido_id)
            asignatura_actual = contenido.unidad_didactica.asignatura
            
            print(f"\n   🎯 CONTENIDO ENCONTRADO:")
            print(f"      ID: {contenido.id}")
            print(f"      Nombre: '{contenido.nombre}'")
            print(f"      Asignatura actual: {asignatura_actual.nombre} (ID: {asignatura_actual.id})")
            
            # 2. Identificar la asignatura correcta
            print(f"\n2. 🎯 IDENTIFICANDO ASIGNATURA CORRECTA:")
            
            # Buscar FISICA I real
            try:
                fisica_i_real = Asignatura.objects.get(nombre='FISICA I')
                print(f"   ✅ FISICA I real encontrada: ID {fisica_i_real.id}")
                
                # ¿Quieres migrar a FISICA I?
                if asignatura_actual.id != fisica_i_real.id:
                    print(f"\n3. 🔄 MIGRANDO A FISICA I:")
                    
                    # Buscar unidad didáctica existente en FISICA I o usar la primera
                    unidades_fisica_i = UnidadDidactica.objects.filter(asignatura=fisica_i_real)
                    
                    if unidades_fisica_i.exists():
                        unidad_didactica_fisica = unidades_fisica_i.first()
                        created = False
                        print(f"   📁 Usando unidad existente: {unidad_didactica_fisica.nombre}")
                    else:
                        unidad_didactica_fisica, created = UnidadDidactica.objects.get_or_create(
                            asignatura=fisica_i_real,
                            nombre=contenido.unidad_didactica.nombre,
                            defaults={
                                'descripcion': contenido.unidad_didactica.descripcion or 'Migrado automáticamente'
                            }
                        )
                    
                    print(f"   📁 Unidad didáctica: {unidad_didactica_fisica.nombre} ({'creada' if created else 'existente'})")
                    
                    # Contar recursos antes de migrar
                    recursos_count = MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).count()
                    titulos_count = Titulo.objects.filter(contenido_analitico=contenido).count()
                    competencias_count = Competencias.objects.filter(contenido_analitico=contenido).count()
                    objetivos_count = ObjetivoPractica.objects.filter(contenido_analitico=contenido).count()
                    
                    print(f"   📊 Recursos a migrar: {recursos_count} recursos, {titulos_count} títulos, {competencias_count} competencias, {objetivos_count} objetivos")
                    
                    # Realizar la migración
                    contenido.unidad_didactica = unidad_didactica_fisica
                    contenido.save()
                    
                    print(f"   ✅ MIGRACIÓN COMPLETADA")
                    print(f"   🔗 Nueva URL: http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/{fisica_i_real.id}/")
                    
                    # Verificar la migración
                    contenido_verificado = ContenidoAnalitico.objects.get(id=contenido.id)
                    nueva_asignatura = contenido_verificado.unidad_didactica.asignatura
                    print(f"   🔍 Verificación: '{contenido_verificado.nombre}' ahora está en {nueva_asignatura.nombre} (ID: {nueva_asignatura.id})")
                    
                else:
                    print(f"   ✅ La práctica YA está en FISICA I correcta")
                    
            except Asignatura.DoesNotExist:
                print(f"   ❌ No se encontró asignatura FISICA I")
                
                # Mostrar todas las asignaturas similares
                print(f"\n   🔍 Asignaturas relacionadas con 'FISICA':")
                asignaturas_fisica = Asignatura.objects.filter(nombre__icontains='FISICA')
                for asig in asignaturas_fisica:
                    contenidos_count = ContenidoAnalitico.objects.filter(unidad_didactica__asignatura=asig).count()
                    print(f"      - {asig.nombre} (ID: {asig.id}) → {contenidos_count} prácticas")
        else:
            print(f"   ❌ No se pudo encontrar el contenido analítico")
    else:
        print("   ❌ No se encontró auditoría reciente")
    
    return True

if __name__ == "__main__":
    migrar_practica_correcta()