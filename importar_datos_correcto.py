"""
Script para importar equipos e insumos usando los campos correctos
Ejecutar con: python manage.py shell -c "exec(open('importar_datos_correcto.py').read())"
"""

import pandas as pd
from datetime import datetime

# Importar modelos
from equipos.models import Equipo
from insumos.models import Insumo
from usuarios.models import Usuario
from core.models import UnidadAcademica, Carrera, Asignatura, GuiaLaboratorio, Practica, Laboratorio

print(f"=== IMPORTACIÓN DE DATOS CON CAMPOS CORRECTOS ===")
print(f"Fecha: {datetime.now()}")

# Obtener datos básicos necesarios
unidad_default = UnidadAcademica.objects.first()
carrera_default = Carrera.objects.first()
asignatura_default = Asignatura.objects.first()
usuario_admin = Usuario.objects.filter(is_superuser=True).first()

if not all([unidad_default, carrera_default, asignatura_default, usuario_admin]):
    print("Error: Faltan datos básicos necesarios")
    print(f"Unidad: {unidad_default}")
    print(f"Carrera: {carrera_default}")
    print(f"Asignatura: {asignatura_default}")
    print(f"Usuario: {usuario_admin}")
    exit()

# Crear dependencias básicas
laboratorio_default, _ = Laboratorio.objects.get_or_create(
    nombre="Laboratorio General",
    defaults={
        'descripcion': 'Laboratorio general para datos importados',
        'ubicacion': 'Edificio principal',
        'capacidad': 30
    }
)

# Crear GuiaLaboratorio básica
guia_default, _ = GuiaLaboratorio.objects.get_or_create(
    nombre="Guía General",
    defaults={
        'descripcion': 'Guía general de laboratorio',
        'objetivo': 'Objetivo general',
        'contenido': 'Contenido básico',
        'unidad_tematica_id': 1,  # Usar ID directo
        'usuario_creador': usuario_admin
    }
)

# Crear Practica básica
practica_default, _ = Practica.objects.get_or_create(
    nombre="Práctica General",
    defaults={
        'descripcion': 'Práctica general de laboratorio',
        'objetivo': 'Objetivo general',
        'procedimiento': 'Procedimiento básico',
        'guia_laboratorio': guia_default,
        'usuario_creador': usuario_admin
    }
)

print(f"Usando:")
print(f"- Unidad: {unidad_default.nombre}")
print(f"- Carrera: {carrera_default.nombre}")
print(f"- Asignatura: {asignatura_default.nombre}")
print(f"- Usuario: {usuario_admin.username}")
print(f"- Laboratorio: {laboratorio_default.nombre}")
print(f"- Guía: {guia_default.nombre}")
print(f"- Práctica: {practica_default.nombre}")

# Importar equipos con campos correctos
print("\n=== IMPORTANDO EQUIPOS ===")
try:
    df_equipos = pd.read_excel('pruebas/DATOS EQUIPOS.xlsx')
    print(f"Filas encontradas: {len(df_equipos)}")
    
    equipos_creados = 0
    for index, row in df_equipos.iterrows():
        try:
            # Obtener descripción del equipo
            descripcion = str(row.get('DESCRIPCION DEL ACTIVO', '')).strip()
            if not descripcion or descripcion == 'nan':
                descripcion = f"Equipo {index + 1}"
            
            # Crear equipo con campos correctos
            equipo, created = Equipo.objects.get_or_create(
                equipo_existente=descripcion[:200],  # Campo correcto
                defaults={
                    # Campos requeridos
                    'unidad_academica': unidad_default,
                    'carrera': carrera_default,
                    'semestre': 1,
                    'asignatura': asignatura_default,
                    'carga_horaria_semanal': 2,
                    'carga_horaria_semestral': 32,
                    'guia_laboratorio': guia_default,
                    'practica': practica_default,
                    'marca': '',
                    'modelo': '',
                    'estado': 'bueno',
                    'numero_unidades': 1,
                    'es_activo_fijo': False,
                    'laboratorio': laboratorio_default,
                    'seccion_area': '',
                    'identificador_aula': '',
                    'equipo_requerido': descripcion[:200],
                    'numero_equipos_requeridos': 1,
                    'usuario_creador': usuario_admin,
                    'responsable_excel': str(row.get('RESPONSABLE', ''))[:200],
                    'observaciones': f"Oficina: {row.get('OFICINA', '')}, CI: {row.get('C.I.', '')}"[:500]
                }
            )
            
            if created:
                equipos_creados += 1
                if equipos_creados % 100 == 0:
                    print(f"Equipos creados: {equipos_creados}")
                    
        except Exception as e:
            print(f"Error en fila {index}: {e}")
            continue
    
    print(f"Equipos importados: {equipos_creados}")
    
except Exception as e:
    print(f"Error al importar equipos: {e}")

# Importar insumos con campos correctos
print("\n=== IMPORTANDO INSUMOS ===")
try:
    df_insumos = pd.read_excel('pruebas/DATOS INSUMOS.xlsm')
    print(f"Filas encontradas: {len(df_insumos)}")
    
    insumos_creados = 0
    for index, row in df_insumos.iterrows():
        try:
            # Obtener nombre del insumo
            nombre = str(row.get('NOMBRE DEL ELEMENTO', '')).strip()
            if not nombre or nombre == 'nan':
                nombre = f"Insumo {index + 1}"
            
            # Determinar categoría
            categoria_str = str(row.get('CATEGORÍA', '')).strip().lower()
            if 'react' in categoria_str or 'quim' in categoria_str:
                categoria = 'reactivos'
            elif 'herr' in categoria_str:
                categoria = 'herramientas'  
            else:
                categoria = 'materiales'
            
            # Crear insumo con campos correctos
            insumo, created = Insumo.objects.get_or_create(
                nombre_elemento=nombre[:200],  # Campo correcto
                defaults={
                    # Campos requeridos
                    'unidad_academica': unidad_default,
                    'laboratorio': laboratorio_default,
                    'categoria': categoria,
                    'descripcion_caracteristicas': '',
                    'marca_modelo': '',
                    'estado': 'bueno',
                    'cantidad': 1,
                    'unidad_medida': 'unidades',
                    'uso_principal': 'practicas',
                    'condiciones_almacenamiento': 'temperatura_ambiente',
                    'ubicacion_fisica': str(row.get('LABORATORIO', ''))[:200],
                    'observaciones': f"Unidad origen: {row.get('UNIDAD ACADÉMICA', '')}"[:500],
                    'carrera': carrera_default,
                    'asignatura': asignatura_default,
                    'guia_laboratorio': guia_default,
                    'practica': practica_default,
                    'usuario_creador': usuario_admin
                }
            )
            
            if created:
                insumos_creados += 1
                
        except Exception as e:
            print(f"Error en fila {index}: {e}")
            continue
    
    print(f"Insumos importados: {insumos_creados}")
    
except Exception as e:
    print(f"Error al importar insumos: {e}")

# Resumen final
print(f"\n=== RESUMEN FINAL ===")
print(f"Total equipos en BD: {Equipo.objects.count()}")
print(f"Total insumos en BD: {Insumo.objects.count()}")
print("¡Importación completada!")

# Mostrar algunos ejemplos
print(f"\n=== EJEMPLOS DE DATOS IMPORTADOS ===")
print("Primeros 5 equipos:")
for equipo in Equipo.objects.all()[:5]:
    print(f"- {equipo.equipo_existente}")

print("Primeros 5 insumos:")
for insumo in Insumo.objects.all()[:5]:
    print(f"- {insumo.nombre_elemento} ({insumo.categoria})")