#!/usr/bin/env python
"""
Script para restaurar las carreras oficiales y arreglar el usuario admin
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import Carrera, UnidadAcademica
from django.contrib.auth.models import User
from django.db import transaction

def crear_carreras_oficiales():
    """Crear las carreras oficiales requeridas"""
    print("📚 Creando carreras oficiales...")
    
    # Lista de carreras requeridas
    carreras_licenciatura = [
        "Ingeniería Civil",
        "Ingeniería Geográfica", 
        "Ingeniería en Sistemas Electrónicos",
        "Ingeniería Industrial",
        "Ingeniería Comercial",
        "Ingeniería de Sistemas",
        "Ingeniería Ambiental",
        "Ingeniería Petrolera",
        "Ingeniería Mecatrónica",
        "Ingeniería en Telecomunicaciones",
        "Ingeniería Financiera",
        "Ingeniería Agroindustrial",
        "Ingeniería Agronómica"
    ]
    
    carreras_tecnicas = [
        "Informática",
        "Sistemas Electrónicos", 
        "Energías Renovables",
        "Construcción Civil",
        "Diseño Gráfico y Comunicación Audiovisual"
    ]
    
    try:
        with transaction.atomic():
            # Obtener una unidad académica por defecto
            unidad_default = UnidadAcademica.objects.first()
            if not unidad_default:
                print("❌ Error: No hay unidades académicas disponibles")
                return False
            
            # Crear carreras de licenciatura
            for nombre_carrera in carreras_licenciatura:
                carrera, created = Carrera.objects.get_or_create(
                    nombre=nombre_carrera,
                    defaults={
                        'descripcion': f'Carrera de {nombre_carrera}',
                        'unidad_academica': unidad_default
                    }
                )
                if created:
                    print(f"   ✅ Creada carrera: {nombre_carrera}")
                else:
                    print(f"   ℹ️  Ya existe: {nombre_carrera}")
            
            # Crear carreras técnicas  
            for nombre_carrera in carreras_tecnicas:
                carrera, created = Carrera.objects.get_or_create(
                    nombre=nombre_carrera,
                    defaults={
                        'descripcion': f'Carrera técnica de {nombre_carrera}',
                        'unidad_academica': unidad_default
                    }
                )
                if created:
                    print(f"   ✅ Creada carrera técnica: {nombre_carrera}")
                else:
                    print(f"   ℹ️  Ya existe: {nombre_carrera}")
            
            print(f"\n📊 Total de carreras en sistema: {Carrera.objects.count()}")
            return True
            
    except Exception as e:
        print(f"❌ Error al crear carreras: {str(e)}")
        return False

def arreglar_usuario_admin():
    """Arreglar el problema del usuario admin"""
    print("🔧 Verificando usuario admin...")
    
    try:
        # Verificar si existe usuario admin
        try:
            admin_user = User.objects.get(username='admin')
            print("   ℹ️  Usuario admin ya existe")
            
            # Verificar que sea superusuario
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
                print("   ✅ Admin promovido a superusuario")
            
            # Cambiar contraseña a una conocida
            admin_user.set_password('admin123')
            admin_user.save()
            print("   ✅ Contraseña de admin actualizada a: admin123")
            
        except User.DoesNotExist:
            # Crear usuario admin nuevo
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@emi.edu.bo',
                password='admin123'
            )
            print("   ✅ Usuario admin creado exitosamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al arreglar usuario admin: {str(e)}")
        return False

def verificar_datos():
    """Verificar que todos los datos estén correctos"""
    print("\n🔍 Verificando datos del sistema...")
    
    print(f"📊 Estadísticas:")
    print(f"   - Unidades Académicas: {UnidadAcademica.objects.count()}")
    print(f"   - Carreras: {Carrera.objects.count()}")
    print(f"   - Usuarios: {User.objects.count()}")
    print(f"   - Superusuarios: {User.objects.filter(is_superuser=True).count()}")
    
    print("\n📚 Carreras registradas:")
    for carrera in Carrera.objects.all().order_by('nombre'):
        print(f"   - {carrera.nombre}")
    
    print("\n👥 Usuarios superusuarios:")
    for user in User.objects.filter(is_superuser=True):
        print(f"   - {user.username} ({user.email})")

def main():
    print("🚀 RESTAURANDO DATOS IMPORTANTES DEL SISTEMA")
    print("=" * 60)
    print("📌 Restaurando:")
    print("   - Carreras oficiales de la EMI")
    print("   - Usuario admin funcional")
    print("=" * 60)
    
    # Arreglar usuario admin
    if arreglar_usuario_admin():
        print("✅ Usuario admin configurado correctamente")
    else:
        print("❌ Error configurando usuario admin")
        return False
    
    # Crear carreras oficiales
    if crear_carreras_oficiales():
        print("✅ Carreras oficiales creadas correctamente")
    else:
        print("❌ Error creando carreras")
        return False
    
    # Verificar datos
    verificar_datos()
    
    print("\n🎉 ¡Restauración completada exitosamente!")
    print("🔑 Credenciales de acceso:")
    print("   - Usuario: admin")
    print("   - Contraseña: admin123")
    print("   - URL: http://127.0.0.1:8000/admin/")
    
    return True

if __name__ == "__main__":
    main()
