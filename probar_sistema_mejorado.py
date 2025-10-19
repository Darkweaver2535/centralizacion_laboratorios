#!/usr/bin/env python3
"""
Script para probar el sistema mejorado de prevención de errores
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import (
    Asignatura, ContenidoAnalitico, AuditoriaCreacionPractica,
    UnidadAcademica, Carrera
)

def analizar_sistema_mejorado():
    """Analizar las mejoras implementadas en el sistema"""
    
    print("🔍 ANÁLISIS DEL SISTEMA MEJORADO")
    print("=" * 60)
    
    # 1. Verificar modelo de auditoría
    print("\n1. 📋 SISTEMA DE AUDITORÍA:")
    total_auditorias = AuditoriaCreacionPractica.objects.count()
    print(f"   • Total registros de auditoría: {total_auditorias}")
    
    if total_auditorias > 0:
        auditoria_reciente = AuditoriaCreacionPractica.objects.order_by('-created_at').first()
        print(f"   • Última auditoría: {auditoria_reciente}")
        print(f"   • Usuario: {auditoria_reciente.usuario}")
        print(f"   • Práctica: {auditoria_reciente.practica_nombre}")
        print(f"   • Asignatura destino: {auditoria_reciente.asignatura_nombre} (ID: {auditoria_reciente.asignatura_id_usado})")
    
    # 2. Verificar asignaturas problemáticas
    print("\n2. ⚠️ ASIGNATURAS PROBLEMÁTICAS DETECTADAS:")
    asignaturas_numericas = Asignatura.objects.filter(nombre__regex=r'^\d+$')
    print(f"   • Asignaturas con nombres numéricos: {asignaturas_numericas.count()}")
    
    for asig in asignaturas_numericas:
        contenidos_count = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=asig
        ).count()
        print(f"     - ID {asig.id}: '{asig.nombre}' → {contenidos_count} prácticas")
    
    # 3. Verificar distribución correcta de prácticas
    print("\n3. 📊 DISTRIBUCIÓN DE PRÁCTICAS POR ASIGNATURA:")
    
    # Obtener todas las asignaturas y contar sus prácticas
    asignaturas_todas = Asignatura.objects.all()
    
    for asig in asignaturas_todas:
        contenidos_count = ContenidoAnalitico.objects.filter(
            unidad_didactica__asignatura=asig
        ).count()
        
        if contenidos_count > 0:  # Solo mostrar las que tienen prácticas
            # Verificar si es una asignatura problemática
            es_problematica = asig.nombre.isdigit()
            icono = "⚠️" if es_problematica else "✅"
            
            print(f"   {icono} {asig.get_nombre_display()} (ID: {asig.id}) → {contenidos_count} prácticas")
    
    # 4. Verificar que PRUEBA LABUBU esté en el lugar correcto
    print("\n4. 🧪 VERIFICACIÓN DE 'PRUEBA LABUBU':")
    labubu_contenidos = ContenidoAnalitico.objects.filter(
        nombre__icontains='PRUEBA LABUBU'
    ).select_related('unidad_didactica__asignatura')
    
    for contenido in labubu_contenidos:
        asig = contenido.unidad_didactica.asignatura
        print(f"   • '{contenido.nombre}' está en: {asig.get_nombre_display()} (ID: {asig.id})")
        print(f"     URL: http://127.0.0.1:8001/dashboard/malla-curricular/asignatura/{asig.id}/")
    
    # 5. Resumen de mejoras implementadas
    print("\n5. 🛡️ MEJORAS DE SEGURIDAD IMPLEMENTADAS:")
    print("   ✅ Validación de unidad académica (solo UALP)")
    print("   ✅ Confirmación JavaScript con información detallada")
    print("   ✅ Logging detallado en consola durante creación")
    print("   ✅ Sistema de auditoría completo con metadatos")
    print("   ✅ Filtrado de asignaturas problemáticas en AJAX")
    print("   ✅ Formato mejorado en dropdowns ([ID:X] Nombre)")
    print("   ✅ Detección de asignaturas similares")
    print("   ✅ Conteo de prácticas existentes por asignatura")
    
    print("\n6. 🎯 FLUJO DE PREVENCIÓN DE ERRORES:")
    print("   1. Frontend: Confirmación detallada antes de envío")
    print("   2. Backend: Validación de unidad académica")
    print("   3. Backend: Logging completo durante creación")
    print("   4. Backend: Registro de auditoría con metadatos")
    print("   5. AJAX: Filtrado de asignaturas problemáticas")
    print("   6. AJAX: Información clara con IDs y conteos")
    
    return True

if __name__ == "__main__":
    analizar_sistema_mejorado()