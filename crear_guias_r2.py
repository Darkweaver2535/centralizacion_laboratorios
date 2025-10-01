#!/usr/bin/env python
"""
Script para crear solo guías de prueba para R2
"""

import os
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import UnidadAcademica, Carrera, Asignatura
from guias.models import GuiaGenerada

def crear_guias_prueba_r2():
    print("=== CREANDO GUÍAS DE PRUEBA PARA R2 ===\n")
    
    # Obtener usuario creador (admin)
    usuario_admin = User.objects.filter(username='admin').first()
    if not usuario_admin:
        print("❌ No se encontró el usuario admin. Creándolo...")
        usuario_admin = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print("✅ Usuario admin creado")
    
    # Crear algunas guías de laboratorio de ejemplo
    carreras = list(Carrera.objects.all()[:5])  # Primeras 5 carreras
    asignaturas = list(Asignatura.objects.all()[:15])  # Primeras 15 asignaturas
    
    guias_creadas = 0
    for i, asignatura in enumerate(asignaturas):
        if asignatura.carrera in carreras:
            guia, created = GuiaGenerada.objects.get_or_create(
                titulo=f"Práctica de {asignatura.get_nombre_display()} - {i+1}",
                carrera=asignatura.carrera,
                asignatura=asignatura,
                defaults={
                    'semestre': str(asignatura.semestre),
                    'contenido_analitico': f'Contenido analítico para práctica de {asignatura.get_nombre_display()}',
                    'unidad_didactica': f'Unidad Didáctica {i+1}',
                    'codigo_guia': f'GUIA-{asignatura.carrera.nombre[:3]}-{asignatura.semestre}-{i+1:02d}',
                    'tipo_practica': random.choice(['laboratorio', 'simulacion', 'proyecto']),
                    'duracion_horas': random.choice([2, 3, 4]),
                    'numero_practica': i + 1,
                    'estado': random.choice(['borrador', 'revision', 'aprobada']),
                    'resultados_esperados': 'Resultados y análisis esperados',
                    'criterios_evaluacion': 'Criterios de evaluación y análisis',
                    'medidas_seguridad': 'Normas de seguridad en el laboratorio',
                    'observaciones': 'Observaciones adicionales para el instructor',
                    'usuario_creador': usuario_admin,
                }
            )
            if created:
                guias_creadas += 1
                print(f"✅ Guía creada: {guia.titulo} ({guia.estado})")
    
    print(f"\n📋 Total guías creadas: {guias_creadas}")
    
    # Mostrar resumen final
    print(f"\n=== RESUMEN FINAL R2 ===")
    print(f"📚 Unidades Académicas: {UnidadAcademica.objects.count()}")
    print(f"🎓 Carreras: {Carrera.objects.count()}")
    print(f"📖 Asignaturas: {Asignatura.objects.count()}")
    print(f"📋 Guías: {GuiaGenerada.objects.count()}")
    
    print(f"\n✅ DATOS DE GUÍAS PARA R2 COMPLETADOS")
    print(f"🚀 El sistema R2 está listo para demostración de filtros dinámicos!")

if __name__ == "__main__":
    crear_guias_prueba_r2()