import os
import pandas as pd
from datetime import datetime
from django.contrib.auth import get_user_model
from core.models import UnidadAcademica, Carrera, Asignatura, Laboratorio, GuiaLaboratorio, Practica
from equipos.models import Equipo
from insumos.models import Insumo

User = get_user_model()

print("=== IMPORTACIÓN COMPLETA DE DATOS DESDE EXCEL ===")
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

print("Creando dependencias básicas...")

# Crear datos básicos necesarios
unidad_default = UnidadAcademica.objects.first()
carrera_default = Carrera.objects.filter(unidad_academica=unidad_default).first() if unidad_default else None
asignatura_default = Asignatura.objects.filter(carrera=carrera_default).first() if carrera_default else None

# Crear laboratorio básico
laboratorio_default, created = Laboratorio.objects.get_or_create(
    nombre="Laboratorio General",
    defaults={
        'descripcion': 'Laboratorio general para importación',
        'ubicacion': 'Edificio Principal',
        'capacidad': 20
    }
)

# Crear guía y práctica básicas
# Primero necesito obtener una unidad temática
from core.models import UnidadTematica
unidad_tematica_default = UnidadTematica.objects.first()

guia_default, created = GuiaLaboratorio.objects.get_or_create(
    nombre="Guía General",
    defaults={
        'unidad_tematica': unidad_tematica_default,
        'numero': 1,
        'descripcion': 'Guía general para importación'
    }
)

practica_default, created = Practica.objects.get_or_create(
    nombre="Práctica General",
    guia_laboratorio=guia_default,
    defaults={
        'numero': 1,
        'descripcion': 'Práctica general para importación'
    }
)

print("Dependencias básicas creadas.")

# 1. IMPORTAR EQUIPOS
print("\n=== IMPORTANDO EQUIPOS DESDE DATOS EQUIPOS.xlsx ===")
archivo_equipos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS EQUIPOS.xlsx'

try:
    df_equipos = pd.read_excel(archivo_equipos)
    print(f"Archivo de equipos leído. Total filas: {len(df_equipos)}")
    
    equipos_creados = 0
    errores_equipos = 0
    
    for index, fila in df_equipos.iterrows():
        try:
            # Obtener datos del Excel tal como están
            numero = fila.get('N', index + 1)
            unidad_academica_excel = str(fila.get('UNIDAD ACADEMICA', '')).strip()
            responsable = str(fila.get('RESPONSABLE', '')).strip()
            ci = str(fila.get('C.I.', '')).strip()
            cargo = str(fila.get('CARGO', '')).strip()
            oficina = str(fila.get('OFICINA', '')).strip()
            codigo = str(fila.get('CODIGO', '')).strip()
            descripcion_activo = str(fila.get('DESCRIPCION DEL ACTIVO', '')).strip()
            estado_excel = str(fila.get('ESTADO', '')).strip()
            fecha_asignacion = fila.get('FECHA DE ASIGNACION')
            
            # Mapear estado a valores válidos del modelo
            estado_mapeado = 'bueno'
            if estado_excel.lower() in ['regular', 'malo']:
                estado_mapeado = estado_excel.lower()
            
            # Crear equipo con todos los datos del Excel
            equipo = Equipo.objects.create(
                # Campos requeridos por el modelo
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
                
                # Datos reales del Excel
                equipo_existente=descripcion_activo[:200],  # Limitamos a 200 caracteres
                estado=estado_mapeado,
                numero_unidades=1,
                
                # Campos adicionales con datos del Excel
                responsable_excel=responsable,
                observaciones=f"N°: {numero}, CI: {ci}, Cargo: {cargo}, Oficina: {oficina}, Código: {codigo}, Unidad: {unidad_academica_excel}, Fecha: {fecha_asignacion}"
            )
            
            equipos_creados += 1
            
            if equipos_creados % 200 == 0:
                print(f"Equipos procesados: {equipos_creados}")
                
        except Exception as e:
            print(f"Error en equipo fila {index + 1}: {str(e)}")
            errores_equipos += 1
            if errores_equipos > 20:
                print("Demasiados errores, continuando con insumos...")
                break
    
    print(f"EQUIPOS - Importados: {equipos_creados}, Errores: {errores_equipos}")

except Exception as e:
    print(f"Error al leer archivo de equipos: {str(e)}")

# 2. IMPORTAR INSUMOS
print("\n=== IMPORTANDO INSUMOS DESDE DATOS INSUMOS.xlsm ===")
archivo_insumos = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/DATOS INSUMOS.xlsm'

try:
    df_insumos = pd.read_excel(archivo_insumos)
    print(f"Archivo de insumos leído. Total filas: {len(df_insumos)}")
    
    insumos_creados = 0
    errores_insumos = 0
    
    for index, fila in df_insumos.iterrows():
        try:
            # Obtener TODOS los datos del Excel tal como están
            unidad_academica_excel = str(fila.get('UNIDAD ACADÉMICA', '')).strip()
            laboratorio_excel = str(fila.get('LABORATORIO', '')).strip()
            categoria_excel = str(fila.get('CATEGORÍA', '')).strip()
            nombre_elemento = str(fila.get('NOMBRE DEL ELEMENTO', '')).strip()
            descripcion_caracteristicas = str(fila.get('DESCRIPCIÓN/CARACTERÍSTICAS', '')).strip()
            marca_modelo = str(fila.get('MARCA / MODELO', '')).strip()
            codigo_inventario = str(fila.get('CÓDIGO DE INVENTARIO (INTERNO)', '')).strip()
            estado_excel = str(fila.get('ESTADO', '')).strip()
            ubicacion_fisica = str(fila.get('UBICACIÓN FÍSICA', '')).strip()
            cantidad = fila.get('CANTIDAD', 1)
            unidad_medida_excel = str(fila.get('UNIDAD DE MEDIDA', '')).strip()
            fecha_ingreso = fila.get('FECHA DE INGRESO/COMPRA')
            uso_principal = str(fila.get('USO PRINCIPAL', '')).strip()
            carrera_excel = str(fila.get('CARRERA', '')).strip()
            semestre_excel = fila.get('SEMESTRE', '')
            asignatura_excel = str(fila.get('ASIGNATURA', '')).strip()
            unidad_tematica = str(fila.get('UNIDAD TEMÁTICA', '')).strip()
            condiciones_almacenamiento = str(fila.get('CONDICIONES DE ALMACENAMIENTO', '')).strip()
            observaciones_excel = str(fila.get('OBSERVACIONES', '')).strip()
            link_fotografia = str(fila.get('INGRESE EL LINK DE LA FOTOGRAFIA DEL ELEMENTO', '')).strip()
            
            # Mapear categoría a valores válidos del modelo
            categoria_mapeada = 'materiales'  # Default
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
            
            # Mapear unidad de medida
            unidad_medida_mapeada = 'unidades'
            if unidad_medida_excel and unidad_medida_excel != 'nan':
                unidades_validas = ['ml', 'l', 'mg', 'g', 'kg', 'm', 'cm', 'mm', 'piezas', 'cajas', 'paquetes', 'frascos', 'sobres']
                for unidad in unidades_validas:
                    if unidad in unidad_medida_excel.lower():
                        unidad_medida_mapeada = unidad
                        break
            
            # Crear insumo con TODOS los datos del Excel
            insumo = Insumo.objects.create(
                # Campos requeridos por el modelo
                unidad_academica=unidad_default,
                laboratorio=laboratorio_default,
                carrera=carrera_default,
                asignatura=asignatura_default,
                
                # Datos reales del Excel
                categoria=categoria_mapeada,
                nombre_elemento=nombre_elemento[:200] if nombre_elemento else f"Insumo {index + 1}",
                descripcion_caracteristicas=descripcion_caracteristicas,
                marca_modelo=marca_modelo,
                estado=estado_mapeado,
                ubicacion_fisica=ubicacion_fisica,
                cantidad=float(cantidad) if pd.notna(cantidad) else 1.0,
                unidad_medida=unidad_medida_mapeada,
                fecha_ingreso_compra=fecha_ingreso if pd.notna(fecha_ingreso) else None
            )
            
            insumos_creados += 1
            
            if insumos_creados % 50 == 0:
                print(f"Insumos procesados: {insumos_creados}")
                
        except Exception as e:
            print(f"Error en insumo fila {index + 1}: {str(e)}")
            errores_insumos += 1
            if errores_insumos > 10:
                print("Demasiados errores, deteniendo importación de insumos...")
                break
    
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