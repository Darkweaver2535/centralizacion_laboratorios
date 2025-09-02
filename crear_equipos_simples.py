#!/usr/bin/env python
"""
Script simplificado para crear equipos básicos sin guías ni prácticas
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *
from equipos.models import Equipo
from usuarios.models import Usuario
import random

def crear_equipos_simples():
    """Crea equipos básicos sin guías ni prácticas"""
    
    print("🚀 Creando equipos básicos (SIMPLIFICADO)")
    print("=" * 50)
    
    # Verificar datos disponibles
    asignaturas = Asignatura.objects.all()
    laboratorios = Laboratorio.objects.all()
    criterios = CriterioDesempeno.objects.all()
    unidades_didacticas = UnidadDidactica.objects.all()
    contenidos = ContenidoAnalitico.objects.all()
    unidades_tematicas = UnidadTematica.objects.all()
    
    print(f"📊 Datos disponibles:")
    print(f"   - Asignaturas: {asignaturas.count()}")
    print(f"   - Laboratorios: {laboratorios.count()}")
    print(f"   - Unidades Temáticas: {unidades_tematicas.count()}")
    
    if not asignaturas.exists():
        print("❌ No hay asignaturas disponibles")
        return
    
    # Obtener un usuario existente
    usuario = Usuario.objects.first()
    if not usuario:
        print("❌ No hay usuarios disponibles. Crear un superusuario primero.")
        return
    
    print(f"👤 Usuario: {usuario.username}")
    
    # Crear guías básicas para cada unidad temática
    guias_creadas = 0
    for unidad_tematica in unidades_tematicas:
        guia, created = GuiaLaboratorio.objects.get_or_create(
            unidad_tematica=unidad_tematica,
            numero=1,
            defaults={
                'nombre': f'Guía - {unidad_tematica.nombre}',
                'descripcion': f'Guía básica para {unidad_tematica.nombre}'
            }
        )
        if created:
            guias_creadas += 1
    
    print(f"📖 Guías creadas: {guias_creadas}")
    
    # Crear prácticas básicas para cada guía
    practicas_creadas = 0
    guias = GuiaLaboratorio.objects.all()
    for guia in guias:
        practica, created = Practica.objects.get_or_create(
            guia_laboratorio=guia,
            numero=1,
            defaults={
                'nombre': f'Práctica - {guia.nombre}',
                'descripcion': f'Práctica básica para {guia.nombre}'
            }
        )
        if created:
            practicas_creadas += 1
    
    print(f"🧪 Prácticas creadas: {practicas_creadas}")
    
    # Nombres de equipos reales
    nombres_equipos = [
        "Microscopio óptico",
        "Multímetro digital", 
        "Osciloscopio",
        "Fuente de alimentación",
        "Balanza analítica",
        "pH-metro",
        "Computadora",
        "Proyector"
    ]
    
    # Marcas y modelos reales
    marcas_modelos = [
        ("FLUKE", "87V"),
        ("TEKTRONIX", "TBS1052B"),
        ("HANNA", "HI2020"),
        ("HP", "ProDesk 400"),
        ("EPSON", "EB-X41"),
        ("METTLER", "ME204")
    ]
    
    equipos_creados = 0
    errores = 0
    
    print("\\n🔄 Creando equipos...")
    
    # Crear equipos para cada asignatura
    for asignatura in asignaturas:
        try:
            # Buscar unidad temática de esta asignatura
            unidad_tematica = unidades_tematicas.filter(asignatura=asignatura).first()
            if not unidad_tematica:
                print(f"⚠️ No hay unidad temática para {asignatura}")
                continue
            
            # Buscar guía y práctica
            guia = GuiaLaboratorio.objects.filter(unidad_tematica=unidad_tematica).first()
            if not guia:
                print(f"⚠️ No hay guía para {asignatura}")
                continue
            
            practica = Practica.objects.filter(guia_laboratorio=guia).first()
            if not practica:
                print(f"⚠️ No hay práctica para {asignatura}")
                continue
            
            # Seleccionar laboratorio (el primero disponible)
            laboratorio = laboratorios.first()
            
            # Obtener datos relacionados
            criterio = criterios.filter(asignatura=asignatura).first()
            unidad_didactica = unidades_didacticas.filter(asignatura=asignatura).first()
            contenido = contenidos.filter(unidad_didactica=unidad_didactica).first() if unidad_didactica else None
            
            # Crear 2-3 equipos por asignatura
            num_equipos = random.randint(2, 3)
            
            for i in range(num_equipos):
                nombre_equipo = random.choice(nombres_equipos)
                marca, modelo = random.choice(marcas_modelos)
                
                equipo = Equipo.objects.create(
                    # Campos obligatorios según el modelo
                    unidad_academica=asignatura.carrera.unidad_academica,
                    carrera=asignatura.carrera,
                    semestre=asignatura.semestre,
                    asignatura=asignatura,
                    carga_horaria_semanal=asignatura.carga_horaria_semanal,
                    carga_horaria_semestral=asignatura.carga_horaria_semestral,
                    criterio_desempeno=criterio,
                    unidad_didactica=unidad_didactica,
                    contenido_analitico=contenido,
                    guia_laboratorio=guia,
                    practica=practica,
                    equipo_existente=f"{nombre_equipo} {i+1}",
                    marca=marca,
                    modelo=modelo,
                    estado=random.choice(['bueno', 'regular', 'malo']),
                    numero_unidades=random.randint(1, 3),
                    es_activo_fijo=random.choice([True, False]),
                    laboratorio=laboratorio,
                    seccion_area=f"Sección {random.choice(['A', 'B', 'C'])}",
                    identificador_aula=f"Aula {random.randint(101, 120)}",
                    equipo_requerido="",
                    numero_equipos_requeridos=0,
                    usuario_creador=usuario,
                    responsable_excel="Coordinador Lab",
                    observaciones=f"Equipo para {asignatura.get_nombre_display()}"
                )
                
                equipos_creados += 1
                print(f"✅ Equipo {equipos_creados}: {equipo.equipo_existente}")
        
        except Exception as e:
            errores += 1
            print(f"❌ Error en {asignatura}: {e}")
    
    # Estadísticas finales
    total_equipos = Equipo.objects.count()
    
    print("\\n" + "=" * 50)
    print("🎉 Equipos creados exitosamente!")
    print(f"   ✅ Equipos nuevos: {equipos_creados}")
    print(f"   📊 Total en BD: {total_equipos}")
    print(f"   📖 Guías: {guias_creadas}")
    print(f"   🧪 Prácticas: {practicas_creadas}")
    print(f"   ⚠️ Errores: {errores}")
    print("\\n✅ Ahora la tabla debe mostrar equipos!")

if __name__ == "__main__":
    crear_equipos_simples()
