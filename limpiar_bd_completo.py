#!/usr/bin/env python
"""
Script más agresivo para limpiar la base de datos y crear una nueva compacta
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.db import connection
from core.models import UnidadAcademica
from insumos.models import TipoInsumo
from django.contrib.auth.models import User
import subprocess

def backup_datos_importantes():
    """Hace un backup de los datos que deben mantenerse"""
    print("💾 Creando backup de datos importantes...")
    
    # Backup de unidades académicas
    unidades = list(UnidadAcademica.objects.all().values())
    
    # Backup de tipos de insumo si existen
    tipos_insumo = list(TipoInsumo.objects.all().values())
    
    # Backup de usuarios (solo superusuarios)
    superusers = list(User.objects.filter(is_superuser=True).values())
    
    return {
        'unidades_academicas': unidades,
        'tipos_insumo': tipos_insumo,
        'superusers': superusers
    }

def crear_bd_limpia():
    """Crea una nueva base de datos limpia"""
    print("🗑️  Eliminando base de datos actual...")
    
    # Cerrar conexiones
    connection.close()
    
    # Eliminar base de datos actual
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("   ✅ Base de datos eliminada")
    
    # Crear nueva base de datos
    print("🏗️  Creando nueva base de datos...")
    result = subprocess.run([
        '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/venv/bin/python', 
        'manage.py', 'migrate'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✅ Nueva base de datos creada")
        return True
    else:
        print(f"   ❌ Error al crear BD: {result.stderr}")
        return False

def restaurar_datos_importantes(backup_data):
    """Restaura los datos importantes en la nueva BD"""
    print("📥 Restaurando datos importantes...")
    
    # Restaurar unidades académicas
    for unidad_data in backup_data['unidades_academicas']:
        unidad = UnidadAcademica(
            nombre=unidad_data['nombre'],
            descripcion=unidad_data['descripcion']
        )
        unidad.save()
        print(f"   ✅ Restaurada unidad: {unidad.nombre}")
    
    # Crear tipos de insumo básicos
    tipos_basicos = [
        {'nombre': 'Reactivo Químico', 'descripcion': 'Reactivos químicos para laboratorio'},
        {'nombre': 'Material de Vidrio', 'descripcion': 'Materiales de vidrio para laboratorio'},
        {'nombre': 'Instrumental', 'descripcion': 'Instrumentos de laboratorio'},
        {'nombre': 'Equipo de Protección', 'descripcion': 'Equipos de protección personal'},
        {'nombre': 'Consumible', 'descripcion': 'Materiales consumibles'}
    ]
    
    for tipo_data in tipos_basicos:
        tipo_insumo, created = TipoInsumo.objects.get_or_create(
            nombre=tipo_data['nombre'],
            defaults={'descripcion': tipo_data['descripcion']}
        )
        if created:
            print(f"   ✅ Creado tipo de insumo: {tipo_insumo.nombre}")
    
    # Crear usuario admin básico
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@laboratorios.com',
            password='admin123'
        )
        print(f"   ✅ Creado usuario admin")

def main():
    print("🚀 LIMPIEZA COMPLETA DE BASE DE DATOS")
    print("=" * 50)
    print("⚠️  ADVERTENCIA: Este proceso eliminará TODA la BD actual")
    print("📌 Se mantendrán únicamente:")
    print("   - Unidades Académicas")
    print("   - Tipos de Insumo básicos")
    print("   - Usuario admin")
    print("=" * 50)
    
    # Verificar tamaño actual
    try:
        result = subprocess.run(['du', '-h', 'db.sqlite3'], capture_output=True, text=True)
        print(f"📊 Tamaño actual: {result.stdout.strip()}")
    except:
        print("📊 No se pudo verificar tamaño actual")
    
    # Hacer backup
    backup_data = backup_datos_importantes()
    print(f"💾 Backup completado: {len(backup_data['unidades_academicas'])} unidades académicas")
    
    # Crear BD limpia
    if crear_bd_limpia():
        # Restaurar datos importantes
        restaurar_datos_importantes(backup_data)
        
        # Verificar nuevo tamaño
        try:
            result = subprocess.run(['du', '-h', 'db.sqlite3'], capture_output=True, text=True)
            print(f"\n📊 Nuevo tamaño: {result.stdout.strip()}")
        except:
            print("\n📊 No se pudo verificar nuevo tamaño")
        
        print("\n🎉 ¡Proceso completado exitosamente!")
        print("📌 La nueva base de datos está lista para usar")
        print("🔑 Usuario admin: admin / admin123")
        
        return True
    else:
        print("\n💥 Error en el proceso")
        return False

if __name__ == "__main__":
    main()
