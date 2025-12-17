#!/usr/bin/env python
"""
Script para probar la creación de un equipo mínimo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from equipos.models import Equipo
from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio

def test_crear_equipo():
    print('\n=== PROBANDO CREACIÓN DE EQUIPO ===')
    
    # Obtener objetos necesarios
    unidad = UnidadAcademica.objects.first()
    carrera = Carrera.objects.first()
    asignatura = Asignatura.objects.first()
    laboratorio = Laboratorio.objects.first()
    
    print(f'Unidad: {unidad}')
    print(f'Carrera: {carrera}')
    print(f'Asignatura: {asignatura}')
    print(f'Laboratorio: {laboratorio}')
    
    # Intentar crear equipo con campos mínimos
    try:
        equipo = Equipo(
            seccion='academico',
            unidad_academica=unidad,
            carrera=carrera,
            semestre=1,
            asignatura=asignatura,
            carga_horaria_semanal=4,
            carga_horaria_semestral=64,
            equipo_existente='Equipo de Prueba',
            laboratorio=laboratorio,
        )
        equipo.save()
        print(f'\n✓ Equipo creado exitosamente: ID {equipo.id}')
        
        # Eliminar el equipo de prueba
        equipo.delete()
        print(f'✓ Equipo de prueba eliminado')
        
    except Exception as e:
        print(f'\n✗ Error al crear equipo: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_crear_equipo()
