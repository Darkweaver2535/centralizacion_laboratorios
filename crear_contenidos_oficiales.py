#!/usr/bin/env python
"""
Script para crear contenidos analíticos básicos usando datos del Excel oficial
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import *

def crear_contenidos_analiticos_desde_excel():
    print("🔧 CREANDO CONTENIDOS ANALÍTICOS DESDE DATOS OFICIALES")
    print("=" * 60)
    
    # Datos extraídos del Excel oficial por asignatura
    contenidos_por_asignatura = {
        'FISICA I': [
            'Movimiento Rectilíneo Uniforme',
            'Movimiento Rectilíneo Uniformemente Variado', 
            'Movimiento Parabólico',
            'Movimiento Circular',
            'Leyes de Newton',
            'Estática de Partículas',
            'Trabajo y Energía',
            'Conservación de la Energía',
            'Cantidad de Movimiento',
            'Colisiones Elásticas e Inelásticas',
            'Momento de Inercia',
            'Rotación de Cuerpos Rígidos',
            'Gravitación Universal',
            'Campo Gravitatorio',
            'Movimiento Armónico Simple',
            'Péndulo Simple',
            'Elasticidad de Materiales',
            'Ley de Hooke'
        ],
        
        'FISICA II': [
            'Temperatura y Dilatación Térmica',
            'Calor Específico',
            'Transferencia de Calor',
            'Primer Principio de la Termodinámica',
            'Segundo Principio de la Termodinámica',
            'Máquinas Térmicas',
            'Propiedades de los Fluidos',
            'Principio de Arquímedes',
            'Ecuación de Continuidad',
            'Ecuación de Bernoulli',
            'Viscosidad',
            'Tensión Superficial'
        ],
        
        'QUIMICA GENERAL': [
            'Balance de Materia sin Reacción',
            'Balance de Materia con Reacción',
            'Composición Centesimal',
            'Fórmula Empírica y Molecular',
            'Concentraciones en Unidades Físicas',
            'Concentraciones en Unidades Químicas',
            'Propiedades Coligativas',
            'Velocidad de Reacción',
            'Orden de Reacción',
            'Catálisis Química',
            'Equilibrio Químico',
            'Constante de Equilibrio',
            'Ácidos y Bases',
            'pH y pOH',
            'Titulaciones Ácido-Base',
            'Celdas Galvánicas',
            'Electrólisis',
            'Potencial de Reducción'
        ],
        
        'FISICOQUIMICA': [
            'Ecuación de Estado de Gases Ideales',
            'Ley de Dalton',
            'Ley de Graham',
            'Humedad Relativa',
            'Ecuación de Van der Waals',
            'Estados Críticos',
            'Principio de Estados Correspondientes',
            'Factor de Compresibilidad'
        ]
    }
    
    contenidos_creados = 0
    
    for nombre_asig, contenidos_lista in contenidos_por_asignatura.items():
        print(f"\n📚 Procesando {nombre_asig}:")
        
        # Buscar la asignatura
        asignatura = Asignatura.objects.filter(nombre__iexact=nombre_asig).first()
        if not asignatura:
            print(f"   ⚠️ Asignatura '{nombre_asig}' no encontrada")
            continue
        
        # Obtener unidades didácticas
        unidades = UnidadDidactica.objects.filter(asignatura=asignatura)
        if not unidades.exists():
            print(f"   ⚠️ No hay unidades didácticas para {nombre_asig}")
            continue
        
        # Distribuir contenidos entre las unidades didácticas disponibles
        contenidos_por_unidad = len(contenidos_lista) // unidades.count()
        if contenidos_por_unidad == 0:
            contenidos_por_unidad = 1
        
        contenido_idx = 0
        
        for unidad in unidades:
            print(f"   📋 {unidad.nombre}:")
            
            # Asignar contenidos a esta unidad
            max_contenidos = min(contenidos_por_unidad + 2, len(contenidos_lista) - contenido_idx)
            
            for i in range(max_contenidos):
                if contenido_idx >= len(contenidos_lista):
                    break
                
                contenido_nombre = contenidos_lista[contenido_idx]
                
                # Crear contenido analítico
                contenido, created = ContenidoAnalitico.objects.get_or_create(
                    nombre=contenido_nombre,
                    unidad_didactica=unidad,
                    defaults={
                        'descripcion': f'Contenido analítico de {contenido_nombre} para {unidad.nombre}'
                    }
                )
                
                if created:
                    print(f"      ✅ Creado: {contenido_nombre}")
                    contenidos_creados += 1
                else:
                    print(f"      ℹ️ Ya existe: {contenido_nombre}")
                
                contenido_idx += 1
            
            if contenido_idx >= len(contenidos_lista):
                break
    
    # Verificar resultado final
    total_contenidos = ContenidoAnalitico.objects.count()
    
    print(f"\n📊 RESULTADO FINAL:")
    print(f"   ✅ Contenidos creados en esta ejecución: {contenidos_creados}")
    print(f"   📊 Total contenidos en base de datos: {total_contenidos}")
    
    if total_contenidos > 0:
        print(f"\n🎉 ¡ÉXITO! El formulario ahora debería mostrar opciones")
        print(f"   🔗 Ve a: http://127.0.0.1:8001/dashboard/malla-curricular/agregar-datos/")
        print(f"   📝 Selecciona: UALP → Una carrera → Una asignatura → Una unidad didáctica")
        print(f"   🧪 Ahora deberías ver opciones en 'Contenido Analítico'")
    else:
        print(f"\n⚠️ Algo salió mal - no hay contenidos disponibles")

    return total_contenidos

if __name__ == "__main__":
    crear_contenidos_analiticos_desde_excel()