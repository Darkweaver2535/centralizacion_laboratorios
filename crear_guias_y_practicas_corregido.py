#!/usr/bin/env python
"""
Script para crear guías de laboratorio y prácticas necesarias
"""

import os
import sys
import django

# Configuración de Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import GuiaLaboratorio, Practica, UnidadTematica, Asignatura

def crear_guias_y_practicas():
    """Crear guías de laboratorio y prácticas básicas para cada asignatura de laboratorio"""
    
    print("🔧 CREANDO GUÍAS DE LABORATORIO Y PRÁCTICAS")
    print("=" * 60)
    
    # Asignaturas de laboratorio
    asignaturas_lab = ['fisica_i', 'quimica_general', 'fisica_ii', 'fisicoquimica']
    
    # Verificar que existan las asignaturas
    for codigo in asignaturas_lab:
        asignatura = Asignatura.objects.filter(nombre=codigo).first()
        if not asignatura:
            print(f"❌ Asignatura no encontrada: {codigo}")
            continue
            
        print(f"✅ Asignatura encontrada: {asignatura.get_nombre_display()}")
        
        # Obtener la primera unidad temática de la asignatura
        unidad_tematica = UnidadTematica.objects.filter(
            asignatura=asignatura
        ).first()
        
        if not unidad_tematica:
            # Crear una unidad temática básica si no existe
            unidad_tematica = UnidadTematica.objects.create(
                asignatura=asignatura,
                nombre=f"Unidad Temática - {asignatura.get_nombre_display()}",
                numero=1,
                descripcion=f"Unidad temática básica para {asignatura.get_nombre_display()}"
            )
            print(f"  📚 Unidad temática creada: {unidad_tematica.nombre}")
        else:
            print(f"  📚 Unidad temática existente: {unidad_tematica.nombre}")
        
        # Crear guía de laboratorio si no existe
        guia, created = GuiaLaboratorio.objects.get_or_create(
            unidad_tematica=unidad_tematica,
            numero=1,
            defaults={
                'nombre': f"Guía de Laboratorio - {asignatura.get_nombre_display()}",
                'descripcion': f"Guía básica de laboratorio para {asignatura.get_nombre_display()}"
            }
        )
        
        if created:
            print(f"  📋 Guía de laboratorio creada: {guia.nombre}")
        else:
            print(f"  📋 Guía de laboratorio existente: {guia.nombre}")
        
        # Crear práctica si no existe
        practica, created = Practica.objects.get_or_create(
            guia_laboratorio=guia,
            numero=1,
            defaults={
                'nombre': f"Práctica 1 - {asignatura.get_nombre_display()}",
                'descripcion': f"Práctica básica de laboratorio para {asignatura.get_nombre_display()}"
            }
        )
        
        if created:
            print(f"  🧪 Práctica creada: {practica.nombre}")
        else:
            print(f"  🧪 Práctica existente: {practica.nombre}")
    
    print("\n📊 RESUMEN FINAL:")
    print("=" * 40)
    print(f"🎓 Unidades Temáticas: {UnidadTematica.objects.count()}")
    print(f"📋 Guías de Laboratorio: {GuiaLaboratorio.objects.count()}")
    print(f"🧪 Prácticas: {Practica.objects.count()}")
    
    return True

if __name__ == "__main__":
    crear_guias_y_practicas()
