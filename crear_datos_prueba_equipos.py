#!/usr/bin/env python
"""
Script para crear datos de prueba de equipos en el sistema
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio
from equipos.models import Equipo

def crear_datos_prueba():
    """Crear datos de prueba para equipos"""
    
    print("🔧 Creando datos de prueba para equipos...")
    
    # 1. Verificar/Crear usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario admin encontrado: {admin_user.username}")
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@emi.edu.bo',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        print(f"✅ Usuario admin creado: {admin_user.username}")
    
    # 2. Verificar/Crear unidades académicas
    unidades_data = [
        ('UASC', 'UASC - Unidad Académica Santa Cruz'),
        ('UARIBE', 'UARIBE - Unidad Académica Riberalta'),
        ('UATROP', 'UATROP - Unidad Académica Trinidad'),
        ('UACBBA', 'UACBBA - Unidad Académica Cochabamba'),
    ]
    
    unidades = {}
    for codigo, nombre in unidades_data:
        unidad, created = UnidadAcademica.objects.get_or_create(
            nombre=codigo,
            defaults={'descripcion': f'Unidad académica {codigo}'}
        )
        unidades[codigo] = unidad
        if created:
            print(f"✅ Unidad académica creada: {unidad}")
        else:
            print(f"📋 Unidad académica existente: {unidad}")
    
    # 3. Verificar/Crear carreras
    carreras_data = [
        ('ING_SISTEMAS', 'Ingeniería de Sistemas', 'UASC'),
        ('ING_INDUSTRIAL', 'Ingeniería Industrial', 'UASC'),
        ('ING_COMERCIAL', 'Ingeniería Comercial', 'UASC'),
        ('ING_CIVIL', 'Ingeniería Civil', 'UASC'),
        ('ING_QUIMICA', 'Ingeniería Química', 'UASC'),
        ('ING_MECATRONICA', 'Ingeniería Mecatrónica', 'UASC'),
    ]
    
    carreras = {}
    for codigo, nombre, unidad_codigo in carreras_data:
        carrera, created = Carrera.objects.get_or_create(
            nombre=codigo,
            defaults={
                'unidad_academica': unidades[unidad_codigo],
                'descripcion': f'Carrera de {nombre}'
            }
        )
        carreras[codigo] = carrera
        if created:
            print(f"✅ Carrera creada: {carrera}")
    
    # 4. Verificar/Crear laboratorios
    laboratorios_data = [
        ('LAB_FISICA_1', 'Laboratorio de Física Piso 1'),
        ('LAB_QUIMICA', 'Laboratorio de Química'),
        ('LAB_SISTEMAS_1', 'Laboratorio de Sistemas Piso 1'),
        ('LAB_MECATRONICA', 'Laboratorio de Mecatrónica'),
        ('LAB_INDUSTRIAL', 'Laboratorio Industrial'),
        ('LAB_CIVIL', 'Laboratorio de Civil'),
    ]
    
    laboratorios = {}
    for codigo, nombre in laboratorios_data:
        laboratorio, created = Laboratorio.objects.get_or_create(
            nombre=codigo,
            defaults={
                'descripcion': nombre,
                'ubicacion': f'Edificio EMI - {nombre}',
                'capacidad': 25
            }
        )
        laboratorios[codigo] = laboratorio
        if created:
            print(f"✅ Laboratorio creado: {laboratorio}")
    
    # 5. Crear asignaturas de prueba
    asignaturas_data = [
        ('Física I', 'ING_SISTEMAS', 1),
        ('Física II', 'ING_SISTEMAS', 2),
        ('Química General', 'ING_QUIMICA', 1),
        ('Circuitos Eléctricos', 'ING_MECATRONICA', 3),
        ('Resistencia de Materiales', 'ING_CIVIL', 4),
        ('Procesos Industriales', 'ING_INDUSTRIAL', 5),
    ]
    
    asignaturas = {}
    for nombre, carrera_codigo, semestre in asignaturas_data:
        asignatura, created = Asignatura.objects.get_or_create(
            nombre=nombre,
            defaults={
                'carrera': carreras[carrera_codigo],
                'semestre': semestre,
                'descripcion': f'Asignatura {nombre} - Semestre {semestre}'
            }
        )
        asignaturas[nombre] = asignatura
        if created:
            print(f"✅ Asignatura creada: {asignatura}")
    
    # 6. Crear unidades temáticas de prueba
    unidades_tematicas = {}
    for asignatura_nombre, asignatura_obj in asignaturas.items():
        unidad_tematica, created = UnidadTematica.objects.get_or_create(
            titulo=f"Unidad Temática I - {asignatura_nombre}",
            defaults={
                'asignatura': asignatura_obj,
                'descripcion': f'Primera unidad temática de {asignatura_nombre}',
                'numero_unidad': 1
            }
        )
        unidades_tematicas[asignatura_nombre] = unidad_tematica
        if created:
            print(f"✅ Unidad temática creada: {unidad_tematica}")
    
    # 7. Crear guías de laboratorio de prueba
    guias_laboratorio = {}
    for asignatura_nombre, unidad_tematica in unidades_tematicas.items():
        guia, created = GuiaLaboratorio.objects.get_or_create(
            titulo=f"Guía Lab 1 - {asignatura_nombre}",
            defaults={
                'unidad_tematica': unidad_tematica,
                'descripcion': f'Primera guía de laboratorio para {asignatura_nombre}',
                'numero_guia': 1
            }
        )
        guias_laboratorio[asignatura_nombre] = guia
        if created:
            print(f"✅ Guía de laboratorio creada: {guia}")
    
    # 8. Crear prácticas de prueba
    practicas = {}
    for asignatura_nombre, guia in guias_laboratorio.items():
        practica, created = Practica.objects.get_or_create(
            titulo=f"Práctica 1 - {asignatura_nombre}",
            defaults={
                'guia_laboratorio': guia,
                'descripcion': f'Primera práctica para {asignatura_nombre}',
                'numero_practica': 1,
                'duracion_horas': 2
            }
        )
        practicas[asignatura_nombre] = practica
        if created:
            print(f"✅ Práctica creada: {practica}")
    
    # 9. Crear equipos de prueba
    equipos_data = [
        {
            'equipo_existente': 'Microscopio Óptico Binocular',
            'marca': 'Olympus',
            'modelo': 'CX23',
            'estado': 'operativo',
            'asignatura': 'Física I',
            'laboratorio': 'LAB_FISICA_1',
            'carrera': 'ING_SISTEMAS',
            'numero_unidades': 5,
        },
        {
            'equipo_existente': 'Balanza Analítica Digital',
            'marca': 'Sartorius',
            'modelo': 'Entris II',
            'estado': 'operativo',
            'asignatura': 'Química General',
            'laboratorio': 'LAB_QUIMICA',
            'carrera': 'ING_QUIMICA',
            'numero_unidades': 3,
        },
        {
            'equipo_existente': 'Osciloscopio Digital',
            'marca': 'Rigol',
            'modelo': 'DS1054Z',
            'estado': 'operativo',
            'asignatura': 'Circuitos Eléctricos',
            'laboratorio': 'LAB_MECATRONICA',
            'carrera': 'ING_MECATRONICA',
            'numero_unidades': 10,
        },
        {
            'equipo_existente': 'Máquina Universal de Ensayos',
            'marca': 'Instron',
            'modelo': '5567',
            'estado': 'mantenimiento',
            'asignatura': 'Resistencia de Materiales',
            'laboratorio': 'LAB_CIVIL',
            'carrera': 'ING_CIVIL',
            'numero_unidades': 1,
        },
        {
            'equipo_existente': 'Computadora de Escritorio',
            'marca': 'HP',
            'modelo': 'EliteDesk 800',
            'estado': 'operativo',
            'asignatura': 'Física I',
            'laboratorio': 'LAB_SISTEMAS_1',
            'carrera': 'ING_SISTEMAS',
            'numero_unidades': 25,
        },
        {
            'equipo_existente': 'Espectrofotómetro UV-Vis',
            'marca': 'Hach',
            'modelo': 'DR3900',
            'estado': 'operativo',
            'asignatura': 'Química General',
            'laboratorio': 'LAB_QUIMICA',
            'carrera': 'ING_QUIMICA',
            'numero_unidades': 2,
        },
        {
            'equipo_existente': 'Robot Industrial',
            'marca': 'KUKA',
            'modelo': 'KR 6 R900',
            'estado': 'nuevo',
            'asignatura': 'Procesos Industriales',
            'laboratorio': 'LAB_INDUSTRIAL',
            'carrera': 'ING_INDUSTRIAL',
            'numero_unidades': 1,
        },
        {
            'equipo_existente': 'Multímetro Digital',
            'marca': 'Fluke',
            'modelo': '87V',
            'estado': 'operativo',
            'asignatura': 'Circuitos Eléctricos',
            'laboratorio': 'LAB_MECATRONICA',
            'carrera': 'ING_MECATRONICA',
            'numero_unidades': 15,
        },
        {
            'equipo_existente': 'Centrifuga de Mesa',
            'marca': 'Hettich',
            'modelo': 'EBA 200',
            'estado': 'usado',
            'asignatura': 'Química General',
            'laboratorio': 'LAB_QUIMICA',
            'carrera': 'ING_QUIMICA',
            'numero_unidades': 4,
        },
        {
            'equipo_existente': 'Proyector Multimedia',
            'marca': 'Epson',
            'modelo': 'PowerLite X41+',
            'estado': 'operativo',
            'asignatura': 'Física II',
            'laboratorio': 'LAB_FISICA_1',
            'carrera': 'ING_SISTEMAS',
            'numero_unidades': 6,
        },
    ]
    
    print("\n🔧 Creando equipos de prueba...")
    equipos_creados = 0
    
    for equipo_data in equipos_data:
        asignatura_nombre = equipo_data['asignatura']
        laboratorio_codigo = equipo_data['laboratorio']
        carrera_codigo = equipo_data['carrera']
        
        # Verificar si el equipo ya existe
        existe_equipo = Equipo.objects.filter(
            equipo_existente=equipo_data['equipo_existente'],
            marca=equipo_data['marca'],
            modelo=equipo_data['modelo']
        ).exists()
        
        if not existe_equipo:
            try:
                equipo = Equipo.objects.create(
                    unidad_academica=unidades['UASC'],  # Todos en UASC por ahora
                    carrera=carreras[carrera_codigo],
                    semestre=asignaturas[asignatura_nombre].semestre,
                    asignatura=asignaturas[asignatura_nombre],
                    carga_horaria_semanal=2,
                    carga_horaria_semestral=32,
                    unidad_tematica=unidades_tematicas[asignatura_nombre],
                    guia_laboratorio=guias_laboratorio[asignatura_nombre],
                    practica=practicas[asignatura_nombre],
                    equipo_existente=equipo_data['equipo_existente'],
                    marca=equipo_data['marca'],
                    modelo=equipo_data['modelo'],
                    estado=equipo_data['estado'],
                    numero_unidades=equipo_data['numero_unidades'],
                    laboratorio=laboratorios[laboratorio_codigo],
                    usuario_creador=admin_user,
                    observaciones=f"Equipo de prueba para {asignatura_nombre}",
                    es_activo_fijo=True,
                    numero_equipos_requeridos=equipo_data['numero_unidades'],
                    equipo_requerido=equipo_data['equipo_existente']
                )
                
                equipos_creados += 1
                print(f"✅ Equipo creado: {equipo.equipo_existente} ({equipo.codigo_inventario})")
                
            except Exception as e:
                print(f"❌ Error creando equipo {equipo_data['equipo_existente']}: {e}")
        else:
            print(f"📋 Equipo ya existe: {equipo_data['equipo_existente']}")
    
    print(f"\n🎉 ¡Datos de prueba creados exitosamente!")
    print(f"📊 Resumen:")
    print(f"   - Unidades académicas: {len(unidades)}")
    print(f"   - Carreras: {len(carreras)}")
    print(f"   - Laboratorios: {len(laboratorios)}")
    print(f"   - Asignaturas: {len(asignaturas)}")
    print(f"   - Equipos nuevos: {equipos_creados}")
    print(f"   - Total equipos en BD: {Equipo.objects.count()}")
    
    print(f"\n🔑 Credenciales de admin:")
    print(f"   Usuario: admin")
    print(f"   Contraseña: admin123")

if __name__ == '__main__':
    crear_datos_prueba()
