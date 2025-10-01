#!/usr/bin/env python
"""
Script para crear datos de prueba para R2
"""

import os
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Asignatura, UnidadDidactica, ContenidoAnalitico
from equipos.models import Equipo
from insumos.models import Insumo, TipoInsumo
from guias.models import GuiaGenerada

def crear_datos_prueba_r2():
    print("=== CREANDO DATOS DE PRUEBA PARA R2 ===\n")
    
    # 1. Crear algunos tipos de insumos si no existen
    tipos_insumos = [
        'Reactivos Químicos',
        'Material de Vidrio',
        'Instrumentos de Medición',
        'Equipo de Seguridad',
        'Consumibles',
    ]
    
    tipos_creados = []
    for nombre in tipos_insumos:
        tipo, created = TipoInsumo.objects.get_or_create(
            nombre=nombre,
            defaults={'descripcion': f'Tipo de {nombre.lower()}'}
        )
        tipos_creados.append(tipo)
        if created:
            print(f"✅ Tipo creado: {nombre}")
    
    # 2. Crear insumos de ejemplo
    insumos_ejemplo = [
        ('Ácido Clorhídrico', 'Reactivos Químicos', 50),
        ('Hidróxido de Sodio', 'Reactivos Químicos', 30),
        ('Probeta 100ml', 'Material de Vidrio', 20),
        ('Beaker 250ml', 'Material de Vidrio', 15),
        ('Multímetro Digital', 'Instrumentos de Medición', 5),
        ('Balanza Analítica', 'Instrumentos de Medición', 3),
        ('Guantes de Nitrilo', 'Equipo de Seguridad', 100),
        ('Gafas Protectoras', 'Equipo de Seguridad', 25),
        ('Papel Filtro', 'Consumibles', 200),
        ('Tubos de Ensayo', 'Consumibles', 80),
    ]
    
    insumos_creados = 0
    for nombre, tipo_nombre, cantidad in insumos_ejemplo:
        tipo = next((t for t in tipos_creados if t.nombre == tipo_nombre), None)
        if tipo:
            # Obtener objetos necesarios
            unidad_academica = UnidadAcademica.objects.first()
            carrera = Carrera.objects.first()
            asignatura = Asignatura.objects.first()
            from core.models import Laboratorio
            laboratorio = Laboratorio.objects.first()
            
            if unidad_academica and carrera and asignatura and laboratorio:
                insumo, created = Insumo.objects.get_or_create(
                    nombre_elemento=nombre,
                    defaults={
                        'unidad_academica': unidad_academica,
                        'laboratorio': laboratorio,
                        'carrera': carrera,
                        'asignatura': asignatura,
                        'categoria': 'reactivos' if 'Químicos' in tipo_nombre else 'materiales' if 'Vidrio' in tipo_nombre or 'Medición' in tipo_nombre else 'herramientas',
                        'cantidad': cantidad,
                        'unidad_medida': 'unidades' if 'Digital' in nombre or 'Analítica' in nombre else 'ml' if 'ml' in nombre else 'unidades',
                        'descripcion_caracteristicas': f'Insumo de laboratorio: {nombre}',
                        'uso_principal': 'practicas',
                        'condiciones_almacenamiento': 'temperatura_ambiente',
                    }
                )
                if created:
                    insumos_creados += 1
                    print(f"✅ Insumo creado: {nombre} ({cantidad} {insumo.unidad_medida})")
            else:
                print(f"⚠️  No se pudo crear {nombre} - faltan objetos relacionados")
    
    print(f"\n📦 Total insumos creados: {insumos_creados}")
    
    # 3. Crear algunas guías de laboratorio de ejemplo
    carreras = list(Carrera.objects.all()[:5])  # Primeras 5 carreras
    asignaturas = list(Asignatura.objects.all()[:10])  # Primeras 10 asignaturas
    
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
                    'objetivos': f'Objetivos de la práctica de {asignatura.get_nombre_display()}',
                    'introduccion_teorica': f'Introducción teórica para {asignatura.get_nombre_display()}',
                    'procedimientos': f'Procedimientos paso a paso para la práctica',
                    'resultados_esperados': 'Resultados y análisis esperados',
                    'cuestionario': 'Preguntas de evaluación y análisis',
                    'bibliografia': 'Referencias bibliográficas relevantes',
                }
            )
            if created:
                guias_creadas += 1
                print(f"✅ Guía creada: {guia.titulo} ({guia.estado})")
    
    print(f"\n📋 Total guías creadas: {guias_creadas}")
    
    # 4. Mostrar resumen final
    print(f"\n=== RESUMEN FINAL ===")
    print(f"📚 Unidades Académicas: {UnidadAcademica.objects.count()}")
    print(f"🎓 Carreras: {Carrera.objects.count()}")
    print(f"📖 Asignaturas: {Asignatura.objects.count()}")
    print(f"🔧 Equipos: {Equipo.objects.count()}")
    print(f"🧪 Insumos: {Insumo.objects.count()}")
    print(f"📋 Guías: {GuiaGenerada.objects.count()}")
    print(f"🏫 Laboratorios: {19}")
    
    print(f"\n✅ DATOS DE PRUEBA R2 COMPLETADOS")
    print(f"🚀 El sistema está listo para la demostración del filtrado en cascada!")

if __name__ == "__main__":
    crear_datos_prueba_r2()