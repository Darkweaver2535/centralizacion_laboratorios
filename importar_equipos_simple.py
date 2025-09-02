#!/usr/bin/env python
"""
Script simplificado para importar equipos del archivo completo.xlsx
Solo crea equipos básicos con los campos que existen en el modelo actual
"""
import os
import django
import pandas as pd

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.models import UnidadAcademica, Carrera, Laboratorio, Asignatura, CriterioDesempeno, UnidadDidactica, ContenidoAnalitico, UnidadTematica, GuiaLaboratorio, Practica
from equipos.models import Equipo
from usuarios.models import Usuario

def importar_equipos_completo():
    """Importar equipos del archivo completo.xlsx"""
    print("🚀 IMPORTANDO EQUIPOS DESDE completo.xlsx")
    print("=" * 60)
    
    try:
        # Leer archivo Excel
        df = pd.read_excel('pruebas/completo.xlsx')
        print(f"📊 Registros en Excel: {len(df)}")
        
        # Obtener datos base necesarios
        usuario_admin = Usuario.objects.filter(is_superuser=True).first()
        asignatura_default = Asignatura.objects.first()
        criterio_default = CriterioDesempeno.objects.first()
        unidad_didactica_default = UnidadDidactica.objects.first()
        contenido_default = ContenidoAnalitico.objects.first()
        
        # Crear datos base si no existen
        if not criterio_default:
            print("⚠️ No hay criterios de desempeño, creando básicos...")
            unidad_tematica = UnidadTematica.objects.create(
                asignatura=asignatura_default,
                numero=1,
                nombre="Unidad Base",
                descripcion="Unidad básica para equipos importados"
            )
            guia = GuiaLaboratorio.objects.create(
                unidad_tematica=unidad_tematica,
                numero=1,
                nombre="Guía Base",
                descripcion="Guía básica para equipos importados"
            )
            practica = Practica.objects.create(
                guia_laboratorio=guia,
                numero=1,
                nombre="Práctica Base",
                descripcion="Práctica básica para equipos importados"
            )
            criterio_default = CriterioDesempeno.objects.create(
                asignatura=asignatura_default,
                codigo="BASE-01",
                nombre="Criterio Base",
                descripcion="Criterio básico para equipos importados"
            )
            unidad_didactica_default = UnidadDidactica.objects.create(
                asignatura=asignatura_default,
                nombre="Unidad Base",
                descripcion="Unidad básica para equipos importados"
            )
            contenido_default = ContenidoAnalitico.objects.create(
                unidad_didactica=unidad_didactica_default,
                nombre="Contenido Base",
                descripcion="Contenido básico para equipos importados"
            )
        else:
            guia = GuiaLaboratorio.objects.first()
            practica = Practica.objects.first()
        
        print(f"✅ Datos base preparados:")
        print(f"   - Usuario: {usuario_admin}")
        print(f"   - Asignatura: {asignatura_default}")
        print(f"   - Criterio: {criterio_default}")
        
        # Mapeo de unidades académicas
        mapeo_unidades = {
            'UALP': 'UALP',
            'UACB': 'UACB',
            'UASC': 'UASC',
            'UATP': 'UATP',
            'UARB': 'UARB'
        }
        
        # Obtener laboratorio por defecto
        laboratorio_default = Laboratorio.objects.first()
        
        # Contadores
        equipos_creados = 0
        errores = 0
        
        print("\n🔄 Procesando equipos...")
        
        for index, row in df.iterrows():
            try:
                # Extraer datos básicos del Excel
                unidad_academica_excel = str(row['UNIDAD ACADEMICA']).strip().upper()
                responsable_excel = str(row['RESPONSABLE']).strip() if pd.notna(row['RESPONSABLE']) else 'Sin responsable'
                descripcion_activo = str(row['DESCRIPCION DEL ACTIVO']).strip() if pd.notna(row['DESCRIPCION DEL ACTIVO']) else f'Activo {index+1}'
                estado_excel = str(row['ESTADO']).strip() if pd.notna(row['ESTADO']) else 'REGULAR'
                
                # Mapear unidad académica
                if unidad_academica_excel not in mapeo_unidades:
                    continue
                    
                unidad_codigo = mapeo_unidades[unidad_academica_excel]
                try:
                    unidad_obj = UnidadAcademica.objects.get(nombre=unidad_codigo)
                except UnidadAcademica.DoesNotExist:
                    continue
                
                # Obtener primera carrera de esa unidad
                carrera_obj = Carrera.objects.filter(unidad_academica=unidad_obj).first()
                if not carrera_obj:
                    continue
                
                # Mapear estado
                estado_mapeado = 'BUENO'
                if 'malo' in estado_excel.lower() or 'dañado' in estado_excel.lower():
                    estado_mapeado = 'MALO'
                elif 'regular' in estado_excel.lower():
                    estado_mapeado = 'REGULAR'
                
                # Crear equipo básico
                equipo = Equipo.objects.create(
                    unidad_academica=unidad_obj,
                    carrera=carrera_obj,
                    semestre=1,
                    asignatura=asignatura_default,
                    carga_horaria_semanal=4,
                    carga_horaria_semestral=80,
                    criterio_desempeno=criterio_default,
                    unidad_didactica=unidad_didactica_default,
                    contenido_analitico=contenido_default,
                    guia_laboratorio=guia,
                    practica=practica,
                    equipo_existente=descripcion_activo[:200],  # Limitar longitud
                    marca='Por definir',
                    modelo='Por definir',
                    estado=estado_mapeado,
                    numero_unidades=1,
                    laboratorio=laboratorio_default,
                    responsable_excel=responsable_excel[:100],  # Limitar longitud
                    usuario_creador=usuario_admin
                )
                
                equipos_creados += 1
                
                if (index + 1) % 100 == 0:
                    print(f"   ⏳ Procesados: {index + 1}/{len(df)} equipos")
                
            except Exception as e:
                errores += 1
                if errores <= 5:  # Solo mostrar primeros 5 errores
                    print(f"   ❌ Error en fila {index + 1}: {str(e)[:100]}...")
        
        print(f"\n🎉 IMPORTACIÓN COMPLETADA")
        print(f"   ✅ Equipos creados: {equipos_creados}")
        print(f"   ❌ Errores: {errores}")
        print(f"   📊 Total equipos en BD: {Equipo.objects.count()}")
        
        # Estadísticas por unidad académica
        print(f"\n📋 EQUIPOS POR UNIDAD ACADÉMICA:")
        for unidad in UnidadAcademica.objects.all():
            count = Equipo.objects.filter(unidad_academica=unidad).count()
            print(f"   • {unidad}: {count} equipos")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    importar_equipos_completo()
