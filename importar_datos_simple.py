import os
import pandas as pd
from datetime import datetime
from django.contrib.auth import get_user_model
from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio, GuiaLaboratorio, Practica
from equipos.models import Equipo
from insumos.models import Insumo

User = get_user_model()

print("=== IMPORTACIÓN DE DATOS DE EQUIPOS E INSUMOS ===")
print(f"Fecha: {datetime.now()}")

# Limpiar datos existentes
print("Limpiando datos existentes...")
Equipo.objects.all().delete()
Insumo.objects.all().delete()
print("Datos limpiados.")

# Crear dependencias básicas
print("Creando dependencias básicas...")

# Usar el primer usuario existente
usuario = User.objects.first()
if not usuario:
    print("Error: No hay usuarios en el sistema")
    exit()

# Crear laboratorio básico
laboratorio_default, created = Laboratorio.objects.get_or_create(
    nombre="Laboratorio General",
    defaults={
        'descripcion': 'Laboratorio general para importación de equipos e insumos',
        'ubicacion': 'Edificio Principal',
        'capacidad': 20
    }
)

# Crear guía de laboratorio básica
guia_default, created = GuiaLaboratorio.objects.get_or_create(
    nombre="Guía General",
    defaults={
        'descripcion': 'Guía de laboratorio general importada desde Excel',
        'autor': 'Sistema',
        'version': '1.0'
    }
)

# Crear práctica básica
practica_default, created = Practica.objects.get_or_create(
    numero_practica=1,
    nombre="Práctica General",
    guia_laboratorio=guia_default,
    defaults={
        'descripcion': 'Práctica general importada desde Excel',
        'duracion_horas': 2,
        'objetivos': 'Objetivos de práctica general'
    }
)

print("Dependencias básicas creadas.")

# Importar equipos
print("\n=== IMPORTANDO EQUIPOS ===")
archivo_equipos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'

try:
    df = pd.read_excel(archivo_equipos)
    print(f"Archivo de equipos leído correctamente. Total filas: {len(df)}")
    
    equipos_creados = 0
    errores = 0
    
    # Obtener la primera unidad, carrera, asignatura y laboratorio disponibles
    unidad_default = UnidadAcademica.objects.first()
    carrera_default = Carrera.objects.filter(unidad_academica=unidad_default).first()
    asignatura_default = Asignatura.objects.filter(carrera=carrera_default).first()
    laboratorio_default = Laboratorio.objects.filter(unidad_academica=unidad_default).first()
    
    if not all([unidad_default, carrera_default, asignatura_default, laboratorio_default]):
        print("Error: No hay datos básicos suficientes en la base de datos")
    else:
        for index, fila in df.iterrows():
            try:
                # Obtener nombre del equipo
                nombre_equipo = str(fila.get('NOMBRE DE EQUIPO EXISTENTE', '')).strip()
                if not nombre_equipo or nombre_equipo == 'nan':
                    nombre_equipo = f"Equipo {index + 1}"
                
                # Crear equipo con valores por defecto
                equipo = Equipo.objects.create(
                    unidad_academica=unidad_default,
                    carrera=carrera_default,
                    semestre=1,
                    asignatura=asignatura_default,
                    carga_horaria_semanal=2,
                    carga_horaria_semestral=32,
                    guia_laboratorio=guia_default,
                    practica=practica_default,
                    equipo_existente=nombre_equipo,
                    marca=str(fila.get('MARCA', '')).strip() if pd.notna(fila.get('MARCA')) else '',
                    modelo=str(fila.get('MODELO', '')).strip() if pd.notna(fila.get('MODELO')) else '',
                    estado='bueno',
                    numero_unidades=1,
                    laboratorio=laboratorio_default,
                    usuario_creador=usuario,
                    responsable_excel=str(fila.get('RESPONSABLE', '')).strip() if pd.notna(fila.get('RESPONSABLE')) else 'Sistema'
                )
                
                equipos_creados += 1
                
                if equipos_creados % 100 == 0:
                    print(f"Equipos procesados: {equipos_creados}")
                
            except Exception as e:
                print(f"Error en fila {index + 1}: {str(e)}")
                errores += 1
                if errores > 10:  # Limitar errores mostrados
                    break
        
        print(f"Equipos importados: {equipos_creados}")
        print(f"Errores: {errores}")

except Exception as e:
    print(f"Error al leer archivo de equipos: {str(e)}")

# Importar insumos
print("\n=== IMPORTANDO INSUMOS ===")
archivo_insumos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm'

try:
    df = pd.read_excel(archivo_insumos)
    print(f"Archivo de insumos leído correctamente. Total filas: {len(df)}")
    
    insumos_creados = 0
    errores = 0
    
    for index, fila in df.iterrows():
        try:
            # Obtener nombre del insumo
            nombre_insumo = str(fila.get('NOMBRE DEL ELEMENTO', '')).strip()
            if not nombre_insumo or nombre_insumo == 'nan':
                nombre_insumo = f"Insumo {index + 1}"
            
            # Crear insumo con valores por defecto
            insumo = Insumo.objects.create(
                unidad_academica=unidad_default,
                laboratorio=laboratorio_default,
                categoria='materiales',
                nombre_elemento=nombre_insumo,
                descripcion_caracteristicas=str(fila.get('DESCRIPCIÓN/CARACTERÍSTICAS', '')).strip() if pd.notna(fila.get('DESCRIPCIÓN/CARACTERÍSTICAS')) else '',
                marca_modelo=str(fila.get('MARCA / MODELO', '')).strip() if pd.notna(fila.get('MARCA / MODELO')) else '',
                estado='bueno',
                cantidad=1,
                unidad_medida='unidades',
                carrera=carrera_default,
                asignatura=asignatura_default
            )
            
            insumos_creados += 1
            
            if insumos_creados % 50 == 0:
                print(f"Insumos procesados: {insumos_creados}")
            
        except Exception as e:
            print(f"Error en fila {index + 1}: {str(e)}")
            errores += 1
            if errores > 10:  # Limitar errores mostrados
                break
    
    print(f"Insumos importados: {insumos_creados}")
    print(f"Errores: {errores}")

except Exception as e:
    print(f"Error al leer archivo de insumos: {str(e)}")

# Verificar importación
print("\n=== VERIFICACIÓN POST-IMPORTACIÓN ===")
total_equipos = Equipo.objects.count()
total_insumos = Insumo.objects.count()

print(f"Total equipos: {total_equipos}")
print(f"Total insumos: {total_insumos}")

print("\n=== DISTRIBUCIÓN POR UNIDAD ===")
for unidad in UnidadAcademica.objects.all():
    equipos_unidad = Equipo.objects.filter(unidad_academica=unidad).count()
    insumos_unidad = Insumo.objects.filter(unidad_academica=unidad).count()
    print(f"{unidad.nombre[:20]}: {equipos_unidad} equipos, {insumos_unidad} insumos")

print("\n=== IMPORTACIÓN COMPLETADA ===")