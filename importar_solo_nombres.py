"""
Script simplificado para importar solo nombres de equipos e insumos
Ejecutar con: python manage.py shell -c "exec(open('importar_solo_nombres.py').read())"
"""

import pandas as pd
from datetime import datetime

# Importar modelos
from equipos.models import Equipo
from insumos.models import Insumo
from usuarios.models import Usuario
from core.models import (
    UnidadAcademica, Carrera, Asignatura, UnidadTematica, 
    GuiaLaboratorio, Practica, Laboratorio
)

print(f"=== IMPORTACIÓN SIMPLIFICADA ===")
print(f"Fecha: {datetime.now()}")

# Obtener datos básicos
unidad_default = UnidadAcademica.objects.first()
carrera_default = Carrera.objects.first()
asignatura_default = Asignatura.objects.first()
usuario_admin = Usuario.objects.filter(is_superuser=True).first()

if not all([unidad_default, carrera_default, asignatura_default, usuario_admin]):
    print("Error: Faltan datos básicos")
    exit()

# Crear jerarquía completa paso a paso
print("Creando dependencias...")

# 1. Crear laboratorio
laboratorio_default, _ = Laboratorio.objects.get_or_create(
    nombre="Laboratorio General",
    defaults={
        'descripcion': 'Laboratorio para datos importados',
        'ubicacion': 'Edificio principal',
        'capacidad': 30
    }
)

# 2. Crear unidad temática
unidad_tematica, _ = UnidadTematica.objects.get_or_create(
    asignatura=asignatura_default,
    numero=1,
    defaults={
        'nombre': 'Unidad General',
        'descripcion': 'Unidad temática para datos importados'
    }
)

# 3. Crear guía de laboratorio
guia_laboratorio, _ = GuiaLaboratorio.objects.get_or_create(
    unidad_tematica=unidad_tematica,
    numero=1,
    defaults={
        'nombre': 'Guía General',
        'descripcion': 'Guía para datos importados'
    }
)

# 4. Crear práctica
practica, _ = Practica.objects.get_or_create(
    guia_laboratorio=guia_laboratorio,
    numero=1,
    defaults={
        'nombre': 'Práctica General',
        'descripcion': 'Práctica para datos importados'
    }
)

print(f"Dependencias creadas exitosamente")

# Importar equipos simplificado
print("\n=== IMPORTANDO EQUIPOS ===")
try:
    df_equipos = pd.read_excel('pruebas/DATOS EQUIPOS.xlsx')
    print(f"Procesando {len(df_equipos)} filas...")
    
    equipos_creados = 0
    for index, row in df_equipos.iterrows():
        try:
            descripcion = str(row.get('DESCRIPCION DEL ACTIVO', '')).strip()
            if not descripcion or descripcion == 'nan':
                descripcion = f"Equipo {index + 1}"
            
            # Verificar si ya existe
            if Equipo.objects.filter(equipo_existente=descripcion[:200]).exists():
                continue
                
            # Crear equipo
            equipo = Equipo.objects.create(
                unidad_academica=unidad_default,
                carrera=carrera_default,
                semestre=1,
                asignatura=asignatura_default,
                carga_horaria_semanal=2,
                carga_horaria_semestral=32,
                guia_laboratorio=guia_laboratorio,
                practica=practica,
                equipo_existente=descripcion[:200],
                marca='',
                modelo='',
                estado='bueno',
                numero_unidades=1,
                es_activo_fijo=False,
                laboratorio=laboratorio_default,
                seccion_area='',
                identificador_aula='',
                equipo_requerido=descripcion[:200],
                numero_equipos_requeridos=1,
                usuario_creador=usuario_admin,
                responsable_excel=str(row.get('RESPONSABLE', ''))[:200],
                observaciones=f"Datos importados. Oficina: {row.get('OFICINA', '')}"[:500]
            )
            
            equipos_creados += 1
            if equipos_creados % 500 == 0:
                print(f"  Equipos procesados: {equipos_creados}")
                
        except Exception as e:
            print(f"Error en equipo fila {index}: {e}")
            continue
    
    print(f"Equipos importados: {equipos_creados}")
    
except Exception as e:
    print(f"Error al procesar equipos: {e}")

# Importar insumos simplificado
print("\n=== IMPORTANDO INSUMOS ===")
try:
    df_insumos = pd.read_excel('pruebas/DATOS INSUMOS.xlsm')
    print(f"Procesando {len(df_insumos)} filas...")
    
    insumos_creados = 0
    for index, row in df_insumos.iterrows():
        try:
            nombre = str(row.get('NOMBRE DEL ELEMENTO', '')).strip()
            if not nombre or nombre == 'nan':
                nombre = f"Insumo {index + 1}"
            
            # Verificar si ya existe
            if Insumo.objects.filter(nombre_elemento=nombre[:200]).exists():
                continue
            
            # Determinar categoría
            categoria_str = str(row.get('CATEGORÍA', '')).strip().lower()
            if 'react' in categoria_str or 'quim' in categoria_str:
                categoria = 'reactivos'
            elif 'herr' in categoria_str:
                categoria = 'herramientas'  
            else:
                categoria = 'materiales'
            
            # Crear insumo
            insumo = Insumo.objects.create(
                unidad_academica=unidad_default,
                laboratorio=laboratorio_default,
                categoria=categoria,
                nombre_elemento=nombre[:200],
                descripcion_caracteristicas='',
                marca_modelo='',
                estado='bueno',
                cantidad=1,
                unidad_medida='unidades',
                uso_principal='practicas',
                condiciones_almacenamiento='temperatura_ambiente',
                ubicacion_fisica=str(row.get('LABORATORIO', ''))[:200],
                observaciones=f"Datos importados. Unidad: {row.get('UNIDAD ACADÉMICA', '')}"[:500],
                carrera=carrera_default,
                asignatura=asignatura_default,
                unidad_tematica=unidad_tematica,  # Agregar este campo
                guia_laboratorio=guia_laboratorio,
                practica=practica,
                usuario_creador=usuario_admin
            )
            
            insumos_creados += 1
                
        except Exception as e:
            print(f"Error en insumo fila {index}: {e}")
            continue
    
    print(f"Insumos importados: {insumos_creados}")
    
except Exception as e:
    print(f"Error al procesar insumos: {e}")

# Resumen final
print(f"\n=== RESUMEN FINAL ===")
print(f"Total equipos: {Equipo.objects.count()}")
print(f"Total insumos: {Insumo.objects.count()}")
print("✅ Importación completada!")

# Mostrar ejemplos
print(f"\n=== EJEMPLOS ===")
print("Primeros 3 equipos:")
for equipo in Equipo.objects.all()[:3]:
    print(f"  - {equipo.equipo_existente}")

print("Primeros 3 insumos:")
for insumo in Insumo.objects.all()[:3]:
    print(f"  - {insumo.nombre_elemento} ({insumo.categoria})")