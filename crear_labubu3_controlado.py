#!/usr/bin/env python3
"""
Prueba controlada para crear LABUBU 3 en FISICA II
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from core.models import (
    UnidadAcademica, Carrera, Asignatura, ContenidoAnalitico, 
    UnidadDidactica, AuditoriaCreacionPractica
)

def crear_labubu3_controlado():
    """Crear LABUBU 3 de manera controlada para detectar problemas"""
    
    print("🧪 PRUEBA CONTROLADA: CREANDO LABUBU 3")
    print("=" * 60)
    
    # 1. Verificar datos necesarios
    print("\n1. 📋 VERIFICANDO DATOS NECESARIOS:")
    
    try:
        ualp = UnidadAcademica.objects.get(id=1)
        print(f"   ✅ Unidad Académica: {ualp.nombre}")
    except UnidadAcademica.DoesNotExist:
        print("   ❌ UALP no encontrada")
        return False
    
    try:
        ing_industrial = Carrera.objects.get(nombre='ING_INDUSTRIAL')
        print(f"   ✅ Carrera: {ing_industrial.get_nombre_display()}")
    except Carrera.DoesNotExist:
        print("   ❌ Ingeniería Industrial no encontrada")
        return False
    
    try:
        fisica_ii = Asignatura.objects.get(nombre='FISICA II')
        print(f"   ✅ Asignatura: {fisica_ii.nombre} (ID: {fisica_ii.id})")
    except Asignatura.DoesNotExist:
        print("   ❌ FISICA II no encontrada")
        return False
    
    # Verificar unidades didácticas
    unidades_fisica_ii = UnidadDidactica.objects.filter(asignatura=fisica_ii)
    if unidades_fisica_ii.exists():
        unidad_destino = unidades_fisica_ii.first()
        print(f"   ✅ Unidad Didáctica: {unidad_destino.nombre}")
    else:
        print("   ⚠️ No hay unidades didácticas, creando una...")
        unidad_destino = UnidadDidactica.objects.create(
            asignatura=fisica_ii,
            nombre="Unidad de Prueba",
            descripcion="Creada para test de LABUBU 3"
        )
        print(f"   ✅ Unidad creada: {unidad_destino.nombre}")
    
    # 2. Simular validaciones backend
    print("\n2. 🔒 SIMULANDO VALIDACIONES BACKEND:")
    
    # Validación 1: UALP
    print(f"   ✅ Validación UALP: Pasó (ID: {ualp.id})")
    
    # Validación 2: Nombre problemático
    nombre_practica = "LABUBU 3"
    if nombre_practica.isdigit() or len(nombre_practica.strip()) <= 3:
        print(f"   ❌ Validación nombre: '{nombre_practica}' es problemático")
        return False
    else:
        print(f"   ✅ Validación nombre: '{nombre_practica}' es válido")
    
    # Validación 3: Lista negra
    nombres_prohibidos = ['168', '169', '170', '171', '172', '173', '174', '175', '176', '177']
    if nombre_practica in nombres_prohibidos:
        print(f"   ❌ Lista negra: '{nombre_practica}' está prohibido")
        return False
    else:
        print(f"   ✅ Lista negra: '{nombre_practica}' no está prohibido")
    
    # Validación 4: Asignatura válida
    if fisica_ii.nombre.isdigit():
        print(f"   ❌ Asignatura problemática: '{fisica_ii.nombre}'")
        return False
    else:
        print(f"   ✅ Asignatura válida: '{fisica_ii.nombre}'")
    
    # 3. Crear el contenido analítico directamente
    print("\n3. 🧪 CREANDO CONTENIDO ANALÍTICO DIRECTAMENTE:")
    
    contenido_existente = ContenidoAnalitico.objects.filter(
        nombre=nombre_practica,
        unidad_didactica__asignatura=fisica_ii
    )
    
    if contenido_existente.exists():
        print(f"   ⚠️ Ya existe '{nombre_practica}' en FISICA II")
        contenido = contenido_existente.first()
    else:
        # Crear nuevo contenido
        contenido = ContenidoAnalitico.objects.create(
            nombre=nombre_practica,
            descripcion=f"Práctica de laboratorio: {nombre_practica}",
            unidad_didactica=unidad_destino
        )
        print(f"   ✅ Contenido creado: ID {contenido.id}")
    
    # 4. Crear componentes básicos
    print("\n4. 📝 CREANDO COMPONENTES BÁSICOS:")
    
    from core.models import Titulo, Competencias, ObjetivoPractica
    
    # Título
    titulo, created = Titulo.objects.get_or_create(
        contenido_analitico=contenido,
        defaults={
            'texto': nombre_practica,
            'orden': 1
        }
    )
    print(f"   ✅ Título: {'creado' if created else 'existente'}")
    
    # Competencia
    competencia, created = Competencias.objects.get_or_create(
        contenido_analitico=contenido,
        defaults={
            'descripcion': f"Desarrollar habilidades prácticas en {nombre_practica}",
            'orden': 1
        }
    )
    print(f"   ✅ Competencia: {'creada' if created else 'existente'}")
    
    # Objetivo
    objetivo, created = ObjetivoPractica.objects.get_or_create(
        contenido_analitico=contenido,
        defaults={
            'descripcion': f"Objetivo de la práctica {nombre_practica}",
            'orden': 1
        }
    )
    print(f"   ✅ Objetivo: {'creado' if created else 'existente'}")
    
    # 5. Crear auditoría manual
    print("\n5. 📊 REGISTRANDO AUDITORÍA:")
    
    User = get_user_model()
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        
        auditoria = AuditoriaCreacionPractica.objects.create(
            usuario=admin_user,
            ip_address='127.0.0.1',
            user_agent='Prueba Controlada',
            
            asignatura=fisica_ii,
            asignatura_nombre=fisica_ii.nombre,
            asignatura_id_usado=fisica_ii.id,
            
            contenido_analitico=contenido,
            practica_nombre=nombre_practica,
            
            unidad_academica_nombre=ualp.nombre,
            carrera_nombre=ing_industrial.get_nombre_display(),
            semestre=fisica_ii.semestre,
            
            asignaturas_similares_detectadas=[],
            confirmacion_usuario=True
        )
        
        print(f"   ✅ Auditoría registrada: ID {auditoria.id}")
        
    except Exception as e:
        print(f"   ⚠️ Error en auditoría: {e}")
    
    # 6. Verificación final
    print("\n6. ✅ VERIFICACIÓN FINAL:")
    
    # Verificar que existe
    contenido_verificado = ContenidoAnalitico.objects.get(id=contenido.id)
    asignatura_final = contenido_verificado.unidad_didactica.asignatura
    
    print(f"   ✅ '{contenido_verificado.nombre}' creado exitosamente")
    print(f"   📚 En asignatura: {asignatura_final.nombre} (ID: {asignatura_final.id})")
    print(f"   🔗 URL: http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/{asignatura_final.id}/")
    
    # Contar total de prácticas en FISICA II
    total_fisica_ii = ContenidoAnalitico.objects.filter(
        unidad_didactica__asignatura=fisica_ii
    ).count()
    print(f"   📊 Total prácticas en FISICA II: {total_fisica_ii}")
    
    return True

if __name__ == "__main__":
    crear_labubu3_controlado()