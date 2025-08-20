#!/usr/bin/env python3
"""
Script para crear datos de prueba para el sistema de reordenamiento de equipos
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append('/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio
from equipos.models import Equipo, TareaReordenamiento, EquipoTarea, LogReordenamiento

def crear_datos_reordenamiento():
    """Crear datos de prueba para el sistema de reordenamiento"""
    
    print("🔧 Creando datos de prueba para el sistema de reordenamiento...")
    
    # Obtener o crear un usuario administrador
    try:
        admin_user = User.objects.get(username='admin')
    except User.DoesNotExist:
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@emi.edu.bo',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            is_staff=True,
            is_superuser=True
        )
        print(f"✅ Usuario administrador creado: {admin_user.username}")
    
    # Crear usuarios adicionales para las tareas
    usuarios = []
    datos_usuarios = [
        ('jperez', 'Juan', 'Pérez', 'jperez@emi.edu.bo'),
        ('mgarcia', 'María', 'García', 'mgarcia@emi.edu.bo'),
        ('cramos', 'Carlos', 'Ramos', 'cramos@emi.edu.bo'),
    ]
    
    for username, first_name, last_name, email in datos_usuarios:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'is_staff': True,
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            print(f"✅ Usuario creado: {user.get_full_name()}")
        usuarios.append(user)
    
    # Obtener algunas unidades académicas existentes
    unidades = list(UnidadAcademica.objects.all()[:3])
    if not unidades:
        print("❌ No se encontraron unidades académicas. Ejecute primero agregar_datos_sistema.py")
        return
    
    # Obtener algunos laboratorios
    laboratorios = list(Laboratorio.objects.all()[:5])
    if not laboratorios:
        print("❌ No se encontraron laboratorios. Creando algunos básicos...")
        # Crear laboratorios básicos
        for i, unidad in enumerate(unidades):
            lab = Laboratorio.objects.create(
                unidad_academica=unidad,
                nombre=f'laboratorio_basico_{i+1}',
                capacidad=20,
                responsable=f'Responsable Lab {i+1}',
                telefono=f'222-{1000+i}',
                email=f'lab{i+1}@emi.edu.bo'
            )
            laboratorios.append(lab)
            print(f"✅ Laboratorio creado: {lab.get_nombre_display()}")
    
    # Obtener algunos equipos existentes
    equipos = list(Equipo.objects.all()[:10])
    if not equipos:
        print("❌ No se encontraron equipos. Creando algunos básicos...")
        # Crear equipos básicos
        carreras = list(Carrera.objects.all()[:3])
        asignaturas = list(Asignatura.objects.all()[:3])
        unidades_tematicas = list(UnidadTematica.objects.all()[:3])
        guias = list(GuiaLaboratorio.objects.all()[:3])
        practicas = list(Practica.objects.all()[:3])
        
        for i in range(10):
            equipo = Equipo.objects.create(
                unidad_academica=unidades[i % len(unidades)],
                carrera=carreras[i % len(carreras)],
                semestre=(i % 8) + 1,
                asignatura=asignaturas[i % len(asignaturas)],
                carga_horaria_semanal=4,
                carga_horaria_semestral=64,
                unidad_tematica=unidades_tematicas[i % len(unidades_tematicas)],
                guia_laboratorio=guias[i % len(guias)],
                practica=practicas[i % len(practicas)],
                equipo_existente=f'Equipo de Prueba {i+1}',
                marca=f'Marca{i+1}',
                modelo=f'Modelo{i+1}',
                estado='operativo',
                numero_unidades=1,
                laboratorio=laboratorios[i % len(laboratorios)],
                usuario_creador=admin_user
            )
            equipos.append(equipo)
            print(f"✅ Equipo creado: {equipo.equipo_existente}")
    
    # Crear tareas de reordenamiento de ejemplo
    tareas_datos = [
        {
            'titulo': 'Reasignación de Equipos de Química',
            'descripcion': 'Reasignar equipos del laboratorio de química básica al laboratorio de química avanzada para optimizar el uso de recursos.',
            'tipo': 'reasignacion',
            'estado': 'pendiente',
            'prioridad': 'alta',
            'usuario_creador': admin_user,
            'usuario_asignado': usuarios[0] if usuarios else admin_user,
            'fecha_fin_estimada': datetime.now() + timedelta(days=7),
        },
        {
            'titulo': 'Transferencia de Equipos entre Unidades',
            'descripcion': 'Transferir equipos de medición desde la Unidad de La Paz hacia la Unidad de Cochabamba según las nuevas necesidades académicas.',
            'tipo': 'transferencia_unidad',
            'estado': 'en_proceso',
            'prioridad': 'media',
            'usuario_creador': admin_user,
            'usuario_asignado': usuarios[1] if len(usuarios) > 1 else admin_user,
            'fecha_fin_estimada': datetime.now() + timedelta(days=14),
            'fecha_inicio': datetime.now() - timedelta(days=2),
            'porcentaje_completado': 30,
        },
        {
            'titulo': 'Reubicación de Equipos de Laboratorio',
            'descripcion': 'Reubicar equipos del laboratorio del piso 1 al piso 3 debido a la remodelación de espacios.',
            'tipo': 'reubicacion',
            'estado': 'completada',
            'prioridad': 'baja',
            'usuario_creador': admin_user,
            'usuario_asignado': usuarios[2] if len(usuarios) > 2 else admin_user,
            'fecha_fin_estimada': datetime.now() - timedelta(days=3),
            'fecha_inicio': datetime.now() - timedelta(days=10),
            'fecha_fin_real': datetime.now() - timedelta(days=1),
            'porcentaje_completado': 100,
        },
        {
            'titulo': 'Actualización de Inventario Semestral',
            'descripcion': 'Revisión y actualización completa del inventario de equipos para el cierre del semestre académico.',
            'tipo': 'actualizacion_inventario',
            'estado': 'pausada',
            'prioridad': 'media',
            'usuario_creador': admin_user,
            'fecha_fin_estimada': datetime.now() + timedelta(days=30),
            'porcentaje_completado': 15,
        },
        {
            'titulo': 'Modificación de Características Técnicas',
            'descripcion': 'Actualizar las características técnicas y especificaciones de equipos según las nuevas normativas.',
            'tipo': 'cambio_caracteristicas',
            'estado': 'pendiente',
            'prioridad': 'urgente',
            'usuario_creador': admin_user,
            'usuario_asignado': usuarios[0] if usuarios else admin_user,
            'fecha_fin_estimada': datetime.now() + timedelta(days=3),
        },
    ]
    
    tareas_creadas = []
    for datos in tareas_datos:
        tarea = TareaReordenamiento.objects.create(**datos)
        tareas_creadas.append(tarea)
        
        # Crear log de creación
        LogReordenamiento.objects.create(
            tarea=tarea,
            usuario=datos['usuario_creador'],
            accion='Tarea Creada',
            descripcion=f'Se creó la tarea: {tarea.titulo}'
        )
        
        print(f"✅ Tarea creada: {tarea.titulo} ({tarea.get_estado_display()})")
    
    # Asignar equipos a algunas tareas
    print("\n🔗 Asignando equipos a las tareas...")
    
    # Tarea 1: Reasignación de Química (3 equipos)
    tarea_quimica = tareas_creadas[0]
    for i in range(3):
        if i < len(equipos):
            EquipoTarea.objects.create(
                tarea=tarea_quimica,
                equipo=equipos[i],
                unidad_academica_origen=equipos[i].unidad_academica,
                laboratorio_origen=equipos[i].laboratorio,
                unidad_academica_destino=unidades[1] if len(unidades) > 1 else unidades[0],
                laboratorio_destino=laboratorios[1] if len(laboratorios) > 1 else laboratorios[0],
            )
    
    LogReordenamiento.objects.create(
        tarea=tarea_quimica,
        usuario=admin_user,
        accion='Equipos Agregados',
        descripcion='Se agregaron 3 equipos a la tarea de reasignación'
    )
    
    # Tarea 2: Transferencia entre unidades (5 equipos, algunos procesados)
    tarea_transferencia = tareas_creadas[1]
    for i in range(3, 8):
        if i < len(equipos):
            equipo_tarea = EquipoTarea.objects.create(
                tarea=tarea_transferencia,
                equipo=equipos[i],
                unidad_academica_origen=equipos[i].unidad_academica,
                laboratorio_origen=equipos[i].laboratorio,
                unidad_academica_destino=unidades[2] if len(unidades) > 2 else unidades[0],
                laboratorio_destino=laboratorios[2] if len(laboratorios) > 2 else laboratorios[0],
            )
            
            # Marcar algunos como procesados
            if i <= 5:
                equipo_tarea.procesado = True
                equipo_tarea.fecha_procesado = datetime.now() - timedelta(hours=i)
                equipo_tarea.save()
    
    LogReordenamiento.objects.create(
        tarea=tarea_transferencia,
        usuario=admin_user,
        accion='Equipos Agregados',
        descripcion='Se agregaron 5 equipos a la tarea de transferencia'
    )
    
    LogReordenamiento.objects.create(
        tarea=tarea_transferencia,
        usuario=usuarios[1] if len(usuarios) > 1 else admin_user,
        accion='Procesamiento Iniciado',
        descripcion='Se inició el procesamiento de equipos'
    )
    
    # Tarea 3: Reubicación (2 equipos, todos procesados)
    tarea_reubicacion = tareas_creadas[2]
    for i in range(8, 10):
        if i < len(equipos):
            equipo_tarea = EquipoTarea.objects.create(
                tarea=tarea_reubicacion,
                equipo=equipos[i],
                unidad_academica_origen=equipos[i].unidad_academica,
                laboratorio_origen=equipos[i].laboratorio,
                laboratorio_destino=laboratorios[3] if len(laboratorios) > 3 else laboratorios[0],
                procesado=True,
                fecha_procesado=datetime.now() - timedelta(days=2),
            )
    
    LogReordenamiento.objects.create(
        tarea=tarea_reubicacion,
        usuario=admin_user,
        accion='Equipos Agregados',
        descripcion='Se agregaron 2 equipos a la tarea de reubicación'
    )
    
    LogReordenamiento.objects.create(
        tarea=tarea_reubicacion,
        usuario=usuarios[2] if len(usuarios) > 2 else admin_user,
        accion='Tarea Completada',
        descripcion='Se completó exitosamente la reubicación de todos los equipos'
    )
    
    print(f"✅ Se asignaron equipos a las tareas")
    
    # Estadísticas finales
    print(f"\n📊 Resumen de datos creados:")
    print(f"   👥 Usuarios: {User.objects.count()}")
    print(f"   🏢 Unidades Académicas: {UnidadAcademica.objects.count()}")
    print(f"   🔬 Laboratorios: {Laboratorio.objects.count()}")
    print(f"   ⚙️  Equipos: {Equipo.objects.count()}")
    print(f"   📋 Tareas de Reordenamiento: {TareaReordenamiento.objects.count()}")
    print(f"   🔗 Asignaciones Equipo-Tarea: {EquipoTarea.objects.count()}")
    print(f"   📝 Logs de Reordenamiento: {LogReordenamiento.objects.count()}")
    
    print(f"\n📋 Tareas por estado:")
    for estado, nombre in TareaReordenamiento.ESTADOS_TAREA:
        count = TareaReordenamiento.objects.filter(estado=estado).count()
        print(f"   {nombre}: {count}")
    
    print(f"\n🎯 Tareas por prioridad:")
    for prioridad, nombre in TareaReordenamiento.PRIORIDADES:
        count = TareaReordenamiento.objects.filter(prioridad=prioridad).count()
        print(f"   {nombre}: {count}")
    
    print(f"\n✅ ¡Datos de prueba creados exitosamente!")
    print(f"   🌐 Accede al sistema de reordenamiento en: /equipos/reordenamiento/")
    print(f"   👤 Usuario admin: admin / admin123")

if __name__ == '__main__':
    crear_datos_reordenamiento()
