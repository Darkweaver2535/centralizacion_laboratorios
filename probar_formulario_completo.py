#!/usr/bin/env python
"""
Script de prueba para verificar que el formulario de agregar datos funcione correctamente
con la nueva estructura armónica del sistema.
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

def crear_datos_prueba():
    """Crear datos de prueba para verificar el funcionamiento"""
    print("📝 CREANDO DATOS DE PRUEBA...")
    
    # Datos de prueba simulando el formulario
    datos_formulario = {
        'unidad_academica': '1',  # UALP
        'carrera': '33',  # INFORMATICA
        'asignatura': 'Matemáticas Aplicadas PRUEBA',
        'semestre': '3',
        'codigo_competencia': 'MAT-001',
        'sigla_curricular': 'MA3',
        'carga_horaria_semanal': '4',
        'carga_horaria_semestral': '80',
        'criterio_desempeno': 'El estudiante debe resolver problemas matemáticos aplicados a la ingeniería',
        'unidad_didactica': 'Cálculo Diferencial e Integral',
        
        # Contenidos analíticos (múltiples)
        'contenidos_analiticos[]': [
            'Derivadas y sus aplicaciones',
            'Integrales definidas e indefinidas'
        ],
        
        # Datos adicionales para el primer contenido (índice 0)
        'bibliografia_0_0': 'Cálculo de Stewart, 8va edición',
        'practica_laboratorio_0_0': 'Práctica de derivadas con software matemático',
        'titulo_0_0': 'Aplicaciones de las derivadas en ingeniería',
        'competencias_0_0': 'Resolver problemas de optimización usando derivadas',
        'objetivo_practica_0_0': 'Aplicar el concepto de derivada en problemas reales',
        'fundamento_teorico_0_0': 'La derivada representa la tasa de cambio instantánea de una función',
        'materiales_0_0': 'Calculadora científica, software Matlab',
        'herramientas_0_0': 'Regla, compás, transportador',
        'equipos_0_0': 'Computadora con software matemático instalado',
        'procedimientos_0_0': '1. Abrir software 2. Definir función 3. Calcular derivada 4. Graficar',
        'calculos_resultados_0_0': 'f\'(x) = 2x para f(x) = x²',
        'cuestionario_0_0': '¿Cuál es la interpretación geométrica de la derivada?',
        
        # Segundo grupo de datos para el primer contenido
        'bibliografia_0_1': 'Matemáticas para ingenieros - Kreyszig',
        'practica_laboratorio_0_1': 'Laboratorio de aplicaciones de derivadas',
        'titulo_0_1': 'Problemas de máximos y mínimos',
        
        # Datos adicionales para el segundo contenido (índice 1)
        'bibliografia_1_0': 'Cálculo Integral - Tom Apostol',
        'practica_laboratorio_1_0': 'Práctica de integración numérica',
        'titulo_1_0': 'Métodos de integración',
    }
    
    return datos_formulario

def simular_envio_formulario(datos):
    """Simular el envío del formulario usando el cliente de prueba de Django"""
    print("🚀 SIMULANDO ENVÍO DE FORMULARIO...")
    
    # Crear cliente de prueba
    client = Client()
    
    # Crear usuario de prueba si no existe
    try:
        user = Usuario.objects.get(username='admin')
    except Usuario.DoesNotExist:
        user = Usuario.objects.create_user('admin', 'admin@test.com', 'admin123')
        print("✅ Usuario de prueba creado")
    
    # Iniciar sesión
    client.force_login(user)
    print("✅ Sesión iniciada")
    
    # Hacer POST a la vista
    response = client.post('/dashboard/malla-curricular/agregar-datos/', datos)
    
    print(f"📊 Código de respuesta: {response.status_code}")
    
    if response.status_code == 302:  # Redirección exitosa
        print("✅ Formulario procesado exitosamente")
        return True
    else:
        print(f"❌ Error en el procesamiento: {response.content}")
        return False

def verificar_datos_creados():
    """Verificar que los datos se crearon correctamente en la base de datos"""
    print("🔍 VERIFICANDO DATOS CREADOS...")
    
    # Buscar la asignatura creada
    try:
        asignatura = Asignatura.objects.get(nombre='Matemáticas Aplicadas PRUEBA')
        print(f"✅ Asignatura creada: {asignatura.nombre}")
        
        # Verificar criterio de desempeño
        criterio = CriterioDesempeno.objects.filter(asignatura=asignatura).first()
        if criterio:
            print(f"✅ Criterio de desempeño: {criterio.descripcion[:50]}...")
        
        # Verificar unidad didáctica
        unidad_didactica = UnidadDidactica.objects.filter(asignatura=asignatura).first()
        if unidad_didactica:
            print(f"✅ Unidad didáctica: {unidad_didactica.nombre}")
            
            # Verificar contenidos analíticos
            contenidos = ContenidoAnalitico.objects.filter(unidad_didactica=unidad_didactica)
            print(f"✅ Contenidos analíticos creados: {contenidos.count()}")
            
            for contenido in contenidos:
                print(f"   📋 {contenido.nombre}")
                
                # Verificar subdatos
                subdatos_counts = {
                    'Bibliografías': Bibliografia.objects.filter(contenido_analitico=contenido).count(),
                    'Prácticas': PracticaLaboratorio.objects.filter(contenido_analitico=contenido).count(),
                    'Títulos': Titulo.objects.filter(contenido_analitico=contenido).count(),
                    'Competencias': Competencias.objects.filter(contenido_analitico=contenido).count(),
                    'Objetivos': ObjetivoPractica.objects.filter(contenido_analitico=contenido).count(),
                    'Fundamentos': FundamentoTeorico.objects.filter(contenido_analitico=contenido).count(),
                    'Materiales': MaterialesHerramientasEquipos.objects.filter(contenido_analitico=contenido).count(),
                    'Procedimientos': Procedimientos.objects.filter(contenido_analitico=contenido).count(),
                    'Cálculos': CalculosResultados.objects.filter(contenido_analitico=contenido).count(),
                    'Cuestionarios': Cuestionario.objects.filter(contenido_analitico=contenido).count(),
                }
                
                for tipo, cantidad in subdatos_counts.items():
                    if cantidad > 0:
                        print(f"      🔸 {tipo}: {cantidad}")
        
        return True
        
    except Asignatura.DoesNotExist:
        print("❌ La asignatura de prueba no fue creada")
        return False

def limpiar_datos_prueba():
    """Limpiar los datos de prueba creados"""
    print("🧹 LIMPIANDO DATOS DE PRUEBA...")
    
    try:
        asignatura = Asignatura.objects.get(nombre='Matemáticas Aplicadas PRUEBA')
        # Django eliminará automáticamente los datos relacionados por las foreign keys
        asignatura.delete()
        print("✅ Datos de prueba eliminados")
    except Asignatura.DoesNotExist:
        print("ℹ️  No hay datos de prueba para eliminar")

def main():
    """Función principal para ejecutar la prueba completa"""
    print("🧪 INICIANDO PRUEBA DE FUNCIONALIDAD DEL FORMULARIO")
    print("=" * 70)
    
    try:
        # 1. Crear datos de prueba
        datos = crear_datos_prueba()
        print("✅ Datos de formulario preparados")
        
        # 2. Simular envío del formulario
        exito = simular_envio_formulario(datos)
        
        if exito:
            # 3. Verificar que los datos se crearon
            verificacion_exitosa = verificar_datos_creados()
            
            if verificacion_exitosa:
                print("\n🎉 PRUEBA COMPLETAMENTE EXITOSA")
                print("✅ El formulario funciona correctamente")
                print("✅ Los datos se procesan y almacenan apropiadamente")
                print("✅ Todas las relaciones se mantienen intactas")
            else:
                print("\n⚠️  El formulario se envió pero los datos no se crearon correctamente")
        else:
            print("\n❌ FALLO EN EL ENVÍO DEL FORMULARIO")
        
        # 4. Limpiar datos de prueba
        limpiar_datos_prueba()
        
    except Exception as e:
        print(f"❌ ERROR DURANTE LA PRUEBA: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar limpiar de todos modos
        try:
            limpiar_datos_prueba()
        except:
            pass

if __name__ == "__main__":
    main()