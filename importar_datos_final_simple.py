import os
import pandas as pd
from datetime import datetime
from django.contrib.auth import get_user_model
from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio, GuiaLaboratorio, Practica, UnidadTematica
from equipos.models import Equipo
from insumos.models import Insumo

User = get_user_model()

print("=== IMPORTACIÓN SIMPLIFICADA DE DATOS DESDE EXCEL ===")
print(f"Fecha: {datetime.now()}")

# Limpiar datos existentes
print("Limpiando datos existentes...")
Equipo.objects.all().delete()
Insumo.objects.all().delete()
print("Datos limpiados.")

# Obtener usuario existente
usuario = User.objects.first()
if not usuario:
    print("Error: No hay usuarios en el sistema")
    exit()

print("Verificando datos básicos...")

# Usar datos existentes o usar la primera unidad disponible
unidad_default = UnidadAcademica.objects.first()
if not unidad_default:
    print("Error: No hay unidades académicas")
    exit()

carrera_default = Carrera.objects.filter(unidad_academica=unidad_default).first()
if not carrera_default:
    print("Error: No hay carreras")
    exit()

asignatura_default = Asignatura.objects.filter(carrera=carrera_default).first()
if not asignatura_default:
    print("Error: No hay asignaturas")
    exit()

# Crear laboratorio básico
laboratorio_default, created = Laboratorio.objects.get_or_create(
    nombre="Laboratorio General",
    defaults={
        'descripcion': 'Laboratorio general para importación',
        'ubicacion': 'Edificio Principal',
        'capacidad': 20
    }
)

# Crear unidad temática básica
unidad_tematica, created = UnidadTematica.objects.get_or_create(
    nombre="Unidad General",
    asignatura=asignatura_default,
    defaults={
        'numero_unidad': 1,
        'descripcion': 'Unidad temática general'
    }
)

# Crear guía básica
guia_default, created = GuiaLaboratorio.objects.get_or_create(
    nombre="Guía General",
    numero=1,
    unidad_tematica=unidad_tematica,
    defaults={
        'descripcion': 'Guía general para importación'
    }
)

# Crear práctica básica
practica_default, created = Practica.objects.get_or_create(
    nombre="Práctica General",
    numero=1,
    guia_laboratorio=guia_default,
    defaults={
        'descripcion': 'Práctica general para importación'
    }
)

print("Datos básicos listos.")

# 1. IMPORTAR EQUIPOS
print("\n=== IMPORTANDO EQUIPOS ===")
archivo_equipos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'

try:
    df_equipos = pd.read_excel(archivo_equipos)
    print(f"Archivo de equipos leído. Total filas: {len(df_equipos)}")
    
    equipos_creados = 0
    errores_equipos = 0
    
    for index, fila in df_equipos.iterrows():
        try:
            # Obtener datos del Excel
            descripcion_activo = str(fila.get('DESCRIPCION DEL ACTIVO', f'Equipo {index + 1}')).strip()
            responsable = str(fila.get('RESPONSABLE', '')).strip()
            unidad_excel = str(fila.get('UNIDAD ACADEMICA', '')).strip()
            estado_excel = str(fila.get('ESTADO', 'bueno')).strip()
            codigo = str(fila.get('CODIGO', '')).strip()
            
            # Mapear estado
            estado_mapeado = 'bueno'
            if 'regular' in estado_excel.lower():
                estado_mapeado = 'regular'
            elif 'malo' in estado_excel.lower():
                estado_mapeado = 'malo'
            
            # Crear equipo
            equipo = Equipo.objects.create(
                unidad_academica=unidad_default,
                carrera=carrera_default,
                semestre=1,
                asignatura=asignatura_default,
                carga_horaria_semanal=2,
                carga_horaria_semestral=32,
                guia_laboratorio=guia_default,
                practica=practica_default,
                laboratorio=laboratorio_default,
                usuario_creador=usuario,
                equipo_existente=descripcion_activo[:200],
                estado=estado_mapeado,
                numero_unidades=1,
                responsable_excel=responsable,
                observaciones=f"Unidad: {unidad_excel}, Código: {codigo}"
            )
            
            equipos_creados += 1
            
            if equipos_creados % 500 == 0:
                print(f"Equipos procesados: {equipos_creados}")
                
        except Exception as e:
            errores_equipos += 1
            if errores_equipos <= 5:  # Solo mostrar primeros 5 errores
                print(f"Error en equipo fila {index + 1}: {str(e)}")
    
    print(f"EQUIPOS - Importados: {equipos_creados}, Errores: {errores_equipos}")

except Exception as e:
    print(f"Error al leer archivo de equipos: {str(e)}")

# 2. IMPORTAR INSUMOS
print("\n=== IMPORTANDO INSUMOS ===")
archivo_insumos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm'

try:
    df_insumos = pd.read_excel(archivo_insumos)
    print(f"Archivo de insumos leído. Total filas: {len(df_insumos)}")
    
    insumos_creados = 0
    errores_insumos = 0
    
    for index, fila in df_insumos.iterrows():
        try:
            # Obtener datos del Excel
            nombre_elemento = str(fila.get('NOMBRE DEL ELEMENTO', f'Insumo {index + 1}')).strip()
            categoria_excel = str(fila.get('CATEGORÍA', 'materiales')).strip()
            marca_modelo = str(fila.get('MARCA / MODELO', '')).strip()
            estado_excel = str(fila.get('ESTADO', 'bueno')).strip()
            cantidad = fila.get('CANTIDAD', 1)
            laboratorio_excel = str(fila.get('LABORATORIO', '')).strip()
            unidad_excel = str(fila.get('UNIDAD ACADÉMICA', '')).strip()
            
            # Mapear categoría
            categoria_mapeada = 'materiales'
            if 'herramienta' in categoria_excel.lower():
                categoria_mapeada = 'herramientas'
            elif 'reactivo' in categoria_excel.lower():
                categoria_mapeada = 'reactivos'
                
            # Mapear estado
            estado_mapeado = 'bueno'
            if 'regular' in estado_excel.lower():
                estado_mapeado = 'regular'
            elif 'malo' in estado_excel.lower():
                estado_mapeado = 'malo'
            elif 'operativo' in estado_excel.lower():
                estado_mapeado = 'bueno'
            
            # Crear insumo
            insumo = Insumo.objects.create(
                unidad_academica=unidad_default,
                laboratorio=laboratorio_default,
                carrera=carrera_default,
                asignatura=asignatura_default,
                categoria=categoria_mapeada,
                nombre_elemento=nombre_elemento[:200],
                marca_modelo=marca_modelo,
                estado=estado_mapeado,
                cantidad=float(cantidad) if pd.notna(cantidad) else 1.0,
                unidad_medida='unidades'
            )
            
            insumos_creados += 1
            
            if insumos_creados % 50 == 0:
                print(f"Insumos procesados: {insumos_creados}")
                
        except Exception as e:
            errores_insumos += 1
            if errores_insumos <= 5:  # Solo mostrar primeros 5 errores
                print(f"Error en insumo fila {index + 1}: {str(e)}")
    
    print(f"INSUMOS - Importados: {insumos_creados}, Errores: {errores_insumos}")

except Exception as e:
    print(f"Error al leer archivo de insumos: {str(e)}")

# 3. VERIFICACIÓN FINAL
print("\n=== VERIFICACIÓN POST-IMPORTACIÓN ===")
total_equipos = Equipo.objects.count()
total_insumos = Insumo.objects.count()

print(f"Total equipos importados: {total_equipos}")
print(f"Total insumos importados: {total_insumos}")

if total_equipos > 0:
    print("\nEjemplos de equipos importados:")
    for equipo in Equipo.objects.all()[:3]:
        print(f"- {equipo.equipo_existente}")

if total_insumos > 0:
    print("\nEjemplos de insumos importados:")
    for insumo in Insumo.objects.all()[:3]:
        print(f"- {insumo.nombre_elemento} ({insumo.categoria})")

print("\n=== IMPORTACIÓN COMPLETADA ===")
print("Los datos están listos para usar en los dropdowns del formulario.")