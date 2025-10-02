#!/usr/bin/env python
"""
Verificación específica de la separación de Herramientas y Equipos
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import Client
from usuarios.models import Usuario
from core.models import *

def verificar_separacion_herramientas_equipos():
    """Verificar que herramientas y equipos se guardan por separado"""
    print("🔧 VERIFICANDO SEPARACIÓN DE HERRAMIENTAS Y EQUIPOS")
    print("=" * 60)
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba si no existe
    try:
        user = Usuario.objects.get(username='admin')
    except Usuario.DoesNotExist:
        user = Usuario.objects.create_user('admin', 'admin@test.com', 'admin123')
    
    # Iniciar sesión
    client.force_login(user)
    
    # Datos de prueba con herramientas y equipos separados
    datos_formulario = {
        'unidad_academica': '1',  # UALP
        'carrera': '33',  # INFORMATICA
        'asignatura': 'Prueba Herramientas Equipos SEPARADOS',
        'semestre': '4',
        'codigo_competencia': 'TEST-001',
        'sigla_curricular': 'TE4',
        'carga_horaria_semanal': '3',
        'carga_horaria_semestral': '60',
        'criterio_desempeno': 'Verificar separación de herramientas y equipos',
        'unidad_didactica': 'Unidad de prueba',
        
        # Contenidos analíticos
        'contenidos_analiticos[]': ['Contenido de prueba separación'],
        
        # Datos adicionales con herramientas y equipos separados
        'bibliografia_0_0': 'Bibliografía de prueba',
        'materiales_0_0': 'Papel, lápiz, borrador',
        'herramientas_0_0': 'Martillo, destornillador, alicate',  # HERRAMIENTAS
        'equipos_0_0': 'Computadora, impresora, monitor',       # EQUIPOS
        'procedimientos_0_0': 'Usar herramientas y equipos por separado',
    }
    
    print("📝 Enviando formulario con herramientas y equipos separados...")
    response = client.post('/dashboard/malla-curricular/agregar-datos/', datos_formulario)
    
    if response.status_code == 302:
        print("✅ Formulario procesado exitosamente")
        
        # Buscar la asignatura creada
        asignatura = Asignatura.objects.get(nombre='Prueba Herramientas Equipos SEPARADOS')
        unidad_didactica = UnidadDidactica.objects.filter(asignatura=asignatura).first()
        contenido = ContenidoAnalitico.objects.filter(unidad_didactica=unidad_didactica).first()
        
        # Verificar herramientas y equipos por separado
        herramientas = MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico=contenido,
            tipo_elemento='herramienta'
        )
        
        equipos = MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico=contenido,
            tipo_elemento='equipo'
        )
        
        materiales = MaterialesHerramientasEquipos.objects.filter(
            contenido_analitico=contenido,
            tipo_elemento='material'
        )
        
        print(f"\n📊 RESULTADOS DE LA VERIFICACIÓN:")
        print(f"   🔨 Herramientas encontradas: {herramientas.count()}")
        for h in herramientas:
            print(f"      - {h.nombre} (tipo: {h.tipo_elemento})")
            
        print(f"   ⚙️  Equipos encontrados: {equipos.count()}")
        for e in equipos:
            print(f"      - {e.nombre} (tipo: {e.tipo_elemento})")
            
        print(f"   📦 Materiales encontrados: {materiales.count()}")
        for m in materiales:
            print(f"      - {m.nombre} (tipo: {m.tipo_elemento})")
        
        # Verificar que se guardaron correctamente
        if herramientas.count() > 0 and equipos.count() > 0:
            print("\n🎉 ¡SEPARACIÓN EXITOSA!")
            print("✅ Herramientas y equipos se guardaron por separado")
            print("✅ Cada tipo tiene su clasificación correcta")
            resultado = True
        else:
            print("\n❌ ERROR EN LA SEPARACIÓN")
            print("❌ No se encontraron herramientas o equipos separados")
            resultado = False
        
        # Limpiar datos de prueba
        asignatura.delete()
        print("\n🧹 Datos de prueba eliminados")
        
        return resultado
    else:
        print(f"❌ Error en el formulario: {response.status_code}")
        return False

def main():
    """Función principal"""
    print("🔧🔩 VERIFICACIÓN DE SEPARACIÓN HERRAMIENTAS/EQUIPOS")
    print("=" * 70)
    
    try:
        resultado = verificar_separacion_herramientas_equipos()
        
        if resultado:
            print("\n🏆 VERIFICACIÓN COMPLETADA CON ÉXITO")
            print("✅ La separación de herramientas y equipos funciona correctamente")
        else:
            print("\n⚠️  VERIFICACIÓN FALLÓ")
            print("❌ Hay problemas con la separación de herramientas y equipos")
            
    except Exception as e:
        print(f"❌ ERROR DURANTE LA VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()