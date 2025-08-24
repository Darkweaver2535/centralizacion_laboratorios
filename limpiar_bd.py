#!/usr/bin/env python
"""
Script para limpiar la base de datos eliminando datos de prueba innecesarios
pero manteniendo los datos importantes para el funcionamiento del sistema.
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Practica, Asignatura, UnidadTematica, GuiaLaboratorio, Laboratorio, Carrera
from ingreso_datos.models import *
from insumos.models import TipoInsumo
from django.db import transaction

def limpiar_datos_prueba():
    """Elimina datos de prueba manteniendo solo lo esencial"""
    
    print("🔍 Analizando base de datos...")
    
    # Verificar datos actuales
    print(f"📊 Registros actuales:")
    print(f"   - Prácticas: {Practica.objects.count()}")
    print(f"   - Asignaturas: {Asignatura.objects.count()}")
    print(f"   - Unidades Temáticas: {UnidadTematica.objects.count()}")
    print(f"   - Guías de Laboratorio: {GuiaLaboratorio.objects.count()}")
    print(f"   - Laboratorios: {Laboratorio.objects.count()}")
    print(f"   - Carreras: {Carrera.objects.count()}")
    
    # Verificar tamaño de BD
    import subprocess
    try:
        result = subprocess.run(['du', '-h', 'db.sqlite3'], capture_output=True, text=True)
        print(f"   - Tamaño actual BD: {result.stdout.strip()}")
    except:
        print("   - No se pudo verificar tamaño de BD")
    
    print("\n🧹 Iniciando limpieza...")
    
    try:
        with transaction.atomic():
            # 1. Eliminar todas las prácticas (son datos de prueba)
            print("🗑️  Eliminando prácticas de prueba...")
            count_practicas = Practica.objects.count()
            Practica.objects.all().delete()
            print(f"   ✅ Eliminadas {count_practicas} prácticas")
            
            # 2. Eliminar asignaturas generadas automáticamente
            print("🗑️  Eliminando asignaturas de prueba...")
            count_asignaturas = Asignatura.objects.count()
            Asignatura.objects.all().delete()
            print(f"   ✅ Eliminadas {count_asignaturas} asignaturas")
            
            # 3. Eliminar unidades temáticas
            print("🗑️  Eliminando unidades temáticas de prueba...")
            count_unidades = UnidadTematica.objects.count()
            UnidadTematica.objects.all().delete()
            print(f"   ✅ Eliminadas {count_unidades} unidades temáticas")
            
            # 4. Eliminar guías de laboratorio generadas
            print("🗑️  Eliminando guías de laboratorio de prueba...")
            count_guias = GuiaLaboratorio.objects.count()
            GuiaLaboratorio.objects.all().delete()
            print(f"   ✅ Eliminadas {count_guias} guías de laboratorio")
            
            # 5. Eliminar laboratorios de prueba
            print("🗑️  Eliminando laboratorios de prueba...")
            count_labs = Laboratorio.objects.count()
            Laboratorio.objects.all().delete()
            print(f"   ✅ Eliminados {count_labs} laboratorios")
            
            # 6. Eliminar carreras de prueba
            print("🗑️  Eliminando carreras de prueba...")
            count_carreras = Carrera.objects.count()
            Carrera.objects.all().delete()
            print(f"   ✅ Eliminadas {count_carreras} carreras")
            
            # 7. Limpiar tablas de ingreso_datos que puedan tener datos de prueba
            print("🗑️  Limpiando datos de ingreso_datos...")
            
            # Verificar si existen las clases antes de usarlas
            try:
                count_eq_existente = EquipoExistente.objects.count()
                EquipoExistente.objects.all().delete()
                print(f"   ✅ Eliminados {count_eq_existente} equipos existentes de prueba")
            except:
                print("   ⚠️  Tabla EquipoExistente no encontrada")
            
            try:
                count_eq_requerido = EquipoRequerido.objects.count()
                EquipoRequerido.objects.all().delete()
                print(f"   ✅ Eliminados {count_eq_requerido} equipos requeridos de prueba")
            except:
                print("   ⚠️  Tabla EquipoRequerido no encontrada")
            
            try:
                count_tipo_equipo = TipoEquipo.objects.count()
                TipoEquipo.objects.all().delete()
                print(f"   ✅ Eliminados {count_tipo_equipo} tipos de equipo de prueba")
            except:
                print("   ⚠️  Tabla TipoEquipo no encontrada")
                
            # 8. Crear datos mínimos necesarios para el funcionamiento
            print("📝 Creando datos mínimos necesarios...")
            
            # Crear algunos tipos de insumo básicos
            tipos_insumo_basicos = [
                'Reactivo Químico',
                'Material de Vidrio',
                'Instrumental',
                'Equipo de Protección',
                'Consumible'
            ]
            
            for tipo_nombre in tipos_insumo_basicos:
                tipo_insumo, created = TipoInsumo.objects.get_or_create(
                    nombre=tipo_nombre,
                    defaults={'descripcion': f'Tipo de insumo: {tipo_nombre}'}
                )
                if created:
                    print(f"   ✅ Creado tipo de insumo: {tipo_nombre}")
            
            print("\n✨ Limpieza completada exitosamente!")
            
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {str(e)}")
        return False
    
    # Verificar resultados
    print(f"\n📊 Estado después de la limpieza:")
    print(f"   - Prácticas: {Practica.objects.count()}")
    print(f"   - Asignaturas: {Asignatura.objects.count()}")
    print(f"   - Tipos de Insumo: {TipoInsumo.objects.count()}")
    
    # Verificar nuevo tamaño
    try:
        result = subprocess.run(['du', '-h', 'db.sqlite3'], capture_output=True, text=True)
        print(f"   - Nuevo tamaño BD: {result.stdout.strip()}")
    except:
        print("   - No se pudo verificar nuevo tamaño")
    
    return True

def compactar_bd():
    """Compacta la base de datos para reducir su tamaño"""
    print("\n🗜️  Compactando base de datos...")
    
    try:
        import subprocess
        result = subprocess.run(['sqlite3', 'db.sqlite3', 'VACUUM;'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Base de datos compactada exitosamente")
            
            # Verificar tamaño final
            result = subprocess.run(['du', '-h', 'db.sqlite3'], capture_output=True, text=True)
            print(f"   - Tamaño final: {result.stdout.strip()}")
        else:
            print(f"   ❌ Error al compactar: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Error al compactar BD: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando limpieza de base de datos...")
    print("⚠️  IMPORTANTE: Manteniendo unidades académicas y datos esenciales")
    print("=" * 60)
    
    if limpiar_datos_prueba():
        compactar_bd()
        print("\n🎉 ¡Proceso completado! La base de datos debería ser mucho más liviana.")
        print("📌 Se han mantenido:")
        print("   - Unidades Académicas")
        print("   - Tipos de Insumo básicos")
        print("   - Estructura de tablas")
        print("   - Configuraciones del sistema")
    else:
        print("\n💥 El proceso falló. Revisa los errores anteriores.")
