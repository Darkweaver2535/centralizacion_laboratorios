"""
Script para importar equipos e insumos desde Excel
Ejecutar con: python manage.py shell -c "exec(open('importar_equipos_insumos_simple.py').read())"
"""

import pandas as pd
from datetime import datetime

# Importar modelos
from equipos.models import Equipo, EstadoEquipo, TipoEquipo
from insumos.models import Insumo, CategoriaInsumo
from usuarios.models import Usuario
from core.models import UnidadAcademica

print(f"=== IMPORTACIÓN DE EQUIPOS E INSUMOS ===")
print(f"Fecha: {datetime.now()}")

# Obtener datos básicos existentes
unidad_default = UnidadAcademica.objects.first()
if not unidad_default:
    print("Error: No hay unidades académicas")
    exit()

usuario_admin = Usuario.objects.filter(is_superuser=True).first()
if not usuario_admin:
    print("Error: No hay usuarios administradores")
    exit()

print(f"Usando unidad: {unidad_default.nombre}")
print(f"Usando usuario: {usuario_admin.username}")

# Crear estados y tipos básicos
estado_activo, _ = EstadoEquipo.objects.get_or_create(
    nombre="Activo",
    defaults={'descripcion': 'Equipo en funcionamiento'}
)

tipo_general, _ = TipoEquipo.objects.get_or_create(
    nombre="General",
    defaults={'descripcion': 'Tipo de equipo general'}
)

categoria_general, _ = CategoriaInsumo.objects.get_or_create(
    nombre="General",
    defaults={'descripcion': 'Categoría general de insumos'}
)

# Importar equipos
print("\n=== IMPORTANDO EQUIPOS ===")
try:
    df_equipos = pd.read_excel('DATOS EQUIPOS.xlsx')
    print(f"Filas encontradas: {len(df_equipos)}")
    print(f"Columnas: {list(df_equipos.columns)}")
    
    equipos_creados = 0
    for index, row in df_equipos.iterrows():
        try:
            # Limpiar datos
            numero = str(row.get('N', index + 1)).strip()
            unidad_str = str(row.get('UNIDAD ACADEMICA', '')).strip()
            responsable = str(row.get('RESPONSABLE', '')).strip()
            ci = str(row.get('C.I.', '')).strip()
            cargo = str(row.get('CARGO', '')).strip()
            oficina = str(row.get('OFICINA', '')).strip()
            codigo = str(row.get('CODIGO', '')).strip()
            descripcion = str(row.get('DESCRIPCION DEL ACTIVO', '')).strip()
            estado_str = str(row.get('ESTADO', '')).strip()
            fecha_str = str(row.get('FECHA DE ASIGNACION', '')).strip()
            
            # Crear nombre del equipo
            if descripcion and descripcion != 'nan':
                nombre = descripcion[:200]  # Limitar longitud
            elif codigo and codigo != 'nan':
                nombre = f"Equipo {codigo}"[:200]
            else:
                nombre = f"Equipo {numero}"[:200]
            
            # Crear el equipo
            equipo, created = Equipo.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': descripcion[:500] if descripcion != 'nan' else '',
                    'marca': '',
                    'modelo': '',
                    'numero_serie': codigo[:100] if codigo != 'nan' else '',
                    'estado': estado_activo,
                    'tipo': tipo_general,
                    'unidad_academica': unidad_default,
                    'responsable': usuario_admin,
                    'ubicacion': oficina[:200] if oficina != 'nan' else '',
                    'observaciones': f"Responsable: {responsable}, CI: {ci}, Cargo: {cargo}"[:500],
                    'activo': True
                }
            )
            
            if created:
                equipos_creados += 1
                if equipos_creados % 100 == 0:
                    print(f"Equipos creados: {equipos_creados}")
                    
        except Exception as e:
            print(f"Error en fila {index}: {e}")
            continue
    
    print(f"Equipos importados exitosamente: {equipos_creados}")
    
except Exception as e:
    print(f"Error al importar equipos: {e}")

# Importar insumos
print("\n=== IMPORTANDO INSUMOS ===")
try:
    df_insumos = pd.read_excel('DATOS INSUMOS.xlsm')
    print(f"Filas encontradas: {len(df_insumos)}")
    print(f"Columnas: {list(df_insumos.columns)}")
    
    insumos_creados = 0
    for index, row in df_insumos.iterrows():
        try:
            # Obtener nombre del insumo
            nombre = str(row.get('NOMBRE DEL ELEMENTO', '')).strip()
            if not nombre or nombre == 'nan':
                nombre = f"Insumo {index + 1}"
            nombre = nombre[:200]  # Limitar longitud
            
            # Otros campos
            unidad_str = str(row.get('UNIDAD ACADÉMICA', '')).strip()
            laboratorio_str = str(row.get('LABORATORIO', '')).strip()
            categoria_str = str(row.get('CATEGORÍA', '')).strip()
            cantidad_str = str(row.get('CANTIDAD', '')).strip()
            
            # Procesar cantidad
            try:
                cantidad = int(float(cantidad_str)) if cantidad_str != 'nan' else 1
            except:
                cantidad = 1
            
            # Crear categoría específica si existe
            if categoria_str and categoria_str != 'nan':
                categoria, _ = CategoriaInsumo.objects.get_or_create(
                    nombre=categoria_str[:100],
                    defaults={'descripcion': f'Categoría {categoria_str}'[:500]}
                )
            else:
                categoria = categoria_general
            
            # Crear el insumo
            insumo, created = Insumo.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'descripcion': f"Laboratorio: {laboratorio_str}"[:500] if laboratorio_str != 'nan' else '',
                    'categoria': categoria,
                    'unidad_academica': unidad_default,
                    'cantidad_disponible': cantidad,
                    'cantidad_minima': 1,
                    'observaciones': f"Unidad origen: {unidad_str}"[:500],
                    'activo': True
                }
            )
            
            if created:
                insumos_creados += 1
                
        except Exception as e:
            print(f"Error en fila {index}: {e}")
            continue
    
    print(f"Insumos importados exitosamente: {insumos_creados}")
    
except Exception as e:
    print(f"Error al importar insumos: {e}")

# Verificar importación
print(f"\n=== RESUMEN FINAL ===")
print(f"Total equipos en BD: {Equipo.objects.count()}")
print(f"Total insumos en BD: {Insumo.objects.count()}")
print(f"Estados de equipo: {EstadoEquipo.objects.count()}")
print(f"Tipos de equipo: {TipoEquipo.objects.count()}")
print(f"Categorías de insumo: {CategoriaInsumo.objects.count()}")
print("Importación completada!")