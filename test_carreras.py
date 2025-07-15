#!/usr/bin/env python3
"""
Script de prueba para verificar que las nuevas carreras están funcionando correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from ingreso_datos.models import Carrera
from ingreso_datos.forms import InformacionAcademicaForm

def test_careers():
    print("=" * 60)
    print("PRUEBA DE CARRERAS ACTUALIZADAS")
    print("=" * 60)
    
    # Verificar carreras en el modelo
    print("\n1. Carreras definidas en el modelo:")
    print("-" * 40)
    for codigo, nombre in Carrera.CARRERAS:
        print(f"   • {nombre} (código: {codigo})")
    
    # Verificar carreras en la base de datos
    print("\n2. Carreras en la base de datos:")
    print("-" * 40)
    carreras_db = Carrera.objects.all().order_by('nombre')
    for carrera in carreras_db:
        print(f"   • {carrera.get_nombre_display()} (código: {carrera.nombre})")
    
    # Verificar carreras en el formulario
    print("\n3. Carreras disponibles en el formulario:")
    print("-" * 40)
    form = InformacionAcademicaForm()
    for codigo, nombre in form.fields['carrera'].choices:
        if codigo:  # Omitir la opción vacía
            print(f"   • {nombre} (código: {codigo})")
    
    # Verificar que las carreras solicitadas estén presentes
    print("\n4. Verificación de carreras solicitadas:")
    print("-" * 40)
    carreras_solicitadas = [
        'Ingeniería Ambiental',
        'Ingeniería Civil',
        'Ingeniería en Sistemas Electrónicos',
        'Ingeniería Comercial',
        'Ingeniería de Sistemas',
        'Ingeniería Agroindustrial',
        'Sistemas Electrónicos',
        'Informática',
        'Construcción Civil',
        'Energías Renovables',
        'Diseño Gráfico y Comunicación Audiovisual'
    ]
    
    carreras_disponibles = [nombre for codigo, nombre in form.fields['carrera'].choices if codigo]
    
    for carrera_solicitada in carreras_solicitadas:
        if carrera_solicitada in carreras_disponibles:
            print(f"   ✓ {carrera_solicitada} - PRESENTE")
        else:
            print(f"   ✗ {carrera_solicitada} - FALTANTE")
    
    print("\n5. Resumen:")
    print("-" * 40)
    print(f"   • Total carreras en modelo: {len(Carrera.CARRERAS)}")
    print(f"   • Total carreras en BD: {carreras_db.count()}")
    print(f"   • Total carreras en formulario: {len(carreras_disponibles)}")
    print(f"   • Carreras solicitadas presentes: {len([c for c in carreras_solicitadas if c in carreras_disponibles])}/{len(carreras_solicitadas)}")
    
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETADA")
    print("=" * 60)

if __name__ == '__main__':
    test_careers()
