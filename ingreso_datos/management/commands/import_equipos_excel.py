import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from ingreso_datos.models import TipoEquipo, EquipoIndividual, UnidadAcademica
import re
import glob

class Command(BaseCommand):
    help = 'Importa equipos desde un archivo Excel con columnas: CODIGO, DESCRIPCION DE ACTIVO, ESTADO'

    def add_arguments(self, parser):
        parser.add_argument(
            'archivo_excel',
            type=str,
            help='Ruta al archivo Excel o carpeta con archivos Excel a importar'
        )
        parser.add_argument(
            '--sheet',
            type=str,
            default=0,
            help='Nombre o índice de la hoja del Excel (por defecto: primera hoja)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin guardar cambios (solo mostrar lo que se haría)'
        )
        parser.add_argument(
            '--header-row',
            type=int,
            default=0,
            help='Número de fila donde están los encabezados (por defecto: 0)'
        )
        parser.add_argument(
            '--all-sheets',
            action='store_true',
            help='Procesar todas las hojas del archivo Excel'
        )
        parser.add_argument(
            '--unidad-academica',
            type=str,
            help='Unidad académica a asociar con los equipos (la_paz, cochabamba, santa_cruz, etc.)'
        )
        parser.add_argument(
            '--carpeta',
            action='store_true',
            help='Procesar todos los archivos Excel de una carpeta'
        )

    def handle(self, *args, **options):
        archivo_excel = options['archivo_excel']
        sheet = options['sheet']
        dry_run = options['dry_run']
        header_row = options['header_row']
        all_sheets = options['all_sheets']
        unidad_academica = options['unidad_academica']
        carpeta = options['carpeta']

        # Validar unidad académica si se especifica
        unidad_academica_obj = None
        if unidad_academica:
            try:
                unidad_academica_obj = UnidadAcademica.objects.get(nombre=unidad_academica)
                self.stdout.write(f'🏢 Asociando equipos con: {unidad_academica_obj.get_nombre_display()}')
            except UnidadAcademica.DoesNotExist:
                raise CommandError(f'Unidad académica "{unidad_academica}" no existe. Unidades disponibles: {", ".join(UnidadAcademica.objects.values_list("nombre", flat=True))}')

        # Determinar archivos a procesar
        archivos_a_procesar = []
        
        if carpeta:
            # Procesar todos los archivos Excel de una carpeta
            if not os.path.isdir(archivo_excel):
                raise CommandError(f'La ruta {archivo_excel} no es una carpeta válida')
            
            # Buscar archivos Excel en la carpeta
            patron_excel = os.path.join(archivo_excel, '*.xlsx')
            patron_xls = os.path.join(archivo_excel, '*.xls')
            
            archivos_xlsx = glob.glob(patron_excel)
            archivos_xls = glob.glob(patron_xls)
            archivos_a_procesar = archivos_xlsx + archivos_xls
            
            if not archivos_a_procesar:
                raise CommandError(f'No se encontraron archivos Excel en la carpeta {archivo_excel}')
            
            self.stdout.write(f'📁 Procesando carpeta: {archivo_excel}')
            self.stdout.write(f'📊 Archivos encontrados: {len(archivos_a_procesar)}')
            for archivo in archivos_a_procesar:
                self.stdout.write(f'  - {os.path.basename(archivo)}')
            
        else:
            # Procesar archivo individual
            if not os.path.exists(archivo_excel):
                raise CommandError(f'El archivo {archivo_excel} no existe')
            
            if not archivo_excel.lower().endswith(('.xlsx', '.xls')):
                raise CommandError('El archivo debe ser un archivo Excel (.xlsx o .xls)')
            
            archivos_a_procesar = [archivo_excel]
            self.stdout.write(f'📄 Procesando archivo: {archivo_excel}')

        # Contadores globales
        total_equipos_procesados = 0
        total_tipos_creados = 0
        total_errores = []
        total_archivos_procesados = 0

        # Procesar cada archivo
        for archivo in archivos_a_procesar:
            self.stdout.write(f'\n🔄 Procesando archivo: {os.path.basename(archivo)}')
            
            try:
                # Determinar qué hojas procesar
                if all_sheets:
                    excel_file = pd.ExcelFile(archivo)
                    sheets_to_process = excel_file.sheet_names
                    self.stdout.write(f'  📋 Procesando todas las hojas: {", ".join(sheets_to_process)}')
                else:
                    # Intentar convertir sheet a entero si es posible
                    try:
                        sheet_param = int(sheet)
                    except ValueError:
                        sheet_param = sheet
                    sheets_to_process = [sheet_param]
                    self.stdout.write(f'  📋 Procesando hoja: {sheet_param}')

                # Procesar cada hoja del archivo
                for sheet_name in sheets_to_process:
                    self.stdout.write(f'\n    � Procesando hoja: {sheet_name}')
                    
                    equipos_hoja, tipos_hoja, errores_hoja = self.procesar_hoja(
                        archivo, sheet_name, header_row, dry_run, unidad_academica_obj
                    )
                    
                    total_equipos_procesados += equipos_hoja
                    total_tipos_creados += tipos_hoja
                    total_errores.extend(errores_hoja)

                total_archivos_procesados += 1
                
            except Exception as e:
                error_msg = f'Error procesando archivo {os.path.basename(archivo)}: {str(e)}'
                total_errores.append(error_msg)
                self.stdout.write(self.style.ERROR(f'    ❌ {error_msg}'))

        # Mostrar resultados finales
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'[DRY-RUN] Resultados simulados totales:'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Importación completada totalmente:'))
        
        self.stdout.write(f'  📁 Archivos procesados: {total_archivos_procesados}/{len(archivos_a_procesar)}')
        self.stdout.write(f'  📦 Equipos procesados: {total_equipos_procesados}')
        self.stdout.write(f'  🏷️  Tipos de equipo creados: {total_tipos_creados}')
        self.stdout.write(f'  ❌ Errores: {len(total_errores)}')
        
        if unidad_academica_obj:
            self.stdout.write(f'  🏢 Unidad académica: {unidad_academica_obj.get_nombre_display()}')

        # Mostrar errores si los hay
        if total_errores:
            self.stdout.write(self.style.ERROR(f'\n❌ Errores encontrados:'))
            for error in total_errores[:20]:  # Mostrar los primeros 20 errores
                self.stdout.write(f'  {error}')
            if len(total_errores) > 20:
                self.stdout.write(f'  ... y {len(total_errores) - 20} errores más')

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))

    def procesar_hoja(self, archivo_excel, sheet_name, header_row, dry_run, unidad_academica=None):
        """Procesa una hoja individual del Excel"""
        try:
            # Leer el archivo Excel
            self.stdout.write(f'  Leyendo hoja: {sheet_name}')
            
            df = pd.read_excel(archivo_excel, sheet_name=sheet_name, header=header_row)
            
            # Si la primera fila contiene los encabezados reales, usarla
            if header_row > 0 and len(df) > 0:
                # Verificar si la primera fila contiene encabezados conocidos
                primera_fila = df.iloc[0].astype(str)
                if any(col in primera_fila.values for col in ['CODIGO', 'DESCRIPCION DE ACTIVO', 'ESTADO']):
                    # Usar la primera fila como encabezados
                    df.columns = primera_fila
                    df = df.drop(df.index[0])  # Eliminar la fila de encabezados
                    df = df.reset_index(drop=True)
            
            # Limpiar nombres de columnas eliminando espacios extra
            df.columns = df.columns.str.strip()
            
            # Verificar que las columnas requeridas existen
            columnas_requeridas = ['CODIGO', 'DESCRIPCION DE ACTIVO', 'ESTADO']
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
            
            if columnas_faltantes:
                self.stdout.write(f'    ⚠️  Columnas faltantes en hoja {sheet_name}: {", ".join(columnas_faltantes)}')
                self.stdout.write(f'    Columnas disponibles: {list(df.columns)}')
                return 0, 0, [f'Hoja {sheet_name}: Columnas faltantes - {", ".join(columnas_faltantes)}']

            # Filtrar filas vacías o con código vacío
            df = df.dropna(subset=['CODIGO'])
            df = df[df['CODIGO'].astype(str).str.strip() != '']
            
            # Mostrar información del archivo
            self.stdout.write(f'    Filas encontradas: {len(df)}')
            
            # Procesar datos
            equipos_procesados = 0
            tipos_creados = 0
            errores = []

            # Mapeo de estados desde Excel a modelo
            mapeo_estados = {
                'BUENO': 'bueno',
                'REGULAR': 'regular',
                'MALO': 'malo',
                'OPERATIVO': 'bueno',
                'INOPERATIVO': 'malo',
                'EN REPARACION': 'regular',
                'EN REPARACIÓN': 'regular',
                'MANTENIMIENTO': 'regular'
            }

            with transaction.atomic():
                if dry_run:
                    self.stdout.write(f'    🧪 MODO DRY-RUN para hoja {sheet_name}')
                
                for index, row in df.iterrows():
                    try:
                        codigo = str(row['CODIGO']).strip()
                        descripcion = str(row['DESCRIPCION DE ACTIVO']).strip()
                        estado_excel = str(row['ESTADO']).strip().upper()
                        
                        # Validar datos obligatorios
                        if not codigo or codigo == 'nan':
                            errores.append(f'Hoja {sheet_name}, Fila {index + 2}: Código vacío')
                            continue
                        
                        if not descripcion or descripcion == 'nan':
                            errores.append(f'Hoja {sheet_name}, Fila {index + 2}: Descripción vacía')
                            continue
                        
                        if not estado_excel or estado_excel == 'nan':
                            errores.append(f'Hoja {sheet_name}, Fila {index + 2}: Estado vacío')
                            continue

                        # Mapear estado
                        estado_modelo = mapeo_estados.get(estado_excel)
                        if not estado_modelo:
                            errores.append(f'Hoja {sheet_name}, Fila {index + 2}: Estado "{estado_excel}" no reconocido')
                            continue

                        # Generar clave de tipo de equipo desde la descripción
                        tipo_equipo_key = self.generar_clave_tipo_equipo(descripcion)
                        
                        # Buscar o crear TipoEquipo
                        tipo_equipo, created = TipoEquipo.objects.get_or_create(
                            nombre=tipo_equipo_key,
                            defaults={
                                'descripcion': descripcion,
                                'capacidad_estudiantes': 1  # Valor por defecto
                            }
                        )
                        
                        if created:
                            tipos_creados += 1
                            if not dry_run:
                                self.stdout.write(f'    ✓ Creado tipo de equipo: {tipo_equipo.get_nombre_display()}')

                        # Verificar si ya existe un equipo con este código
                        if EquipoIndividual.objects.filter(codigo=codigo).exists():
                            errores.append(f'Hoja {sheet_name}, Fila {index + 2}: Ya existe un equipo con código "{codigo}"')
                            continue

                        # Crear EquipoIndividual
                        # Determinar estado operativo basado en estado físico
                        if estado_modelo == 'bueno':
                            estado_operativo = 'operativo'
                        elif estado_modelo == 'regular':
                            estado_operativo = 'operativo'  # Regular puede seguir siendo operativo
                        else:  # malo
                            estado_operativo = 'mantenimiento'
                        
                        if not dry_run:
                            equipo_individual = EquipoIndividual.objects.create(
                                tipo_equipo=tipo_equipo,
                                codigo=codigo,
                                estado_fisico=estado_modelo,
                                estado_operativo=estado_operativo,
                                unidad_academica=unidad_academica,
                                observaciones=f'Importado desde Excel ({sheet_name}): {descripcion}'
                            )
                            equipos_procesados += 1
                            
                            if equipos_procesados % 10 == 0:
                                self.stdout.write(f'    Procesados {equipos_procesados} equipos...')
                        else:
                            equipos_procesados += 1
                            ua_text = f' (UA: {unidad_academica.get_nombre_display()})' if unidad_academica else ''
                            self.stdout.write(f'    [DRY-RUN] Crearía equipo: {codigo} - {descripcion} - {estado_modelo}{ua_text}')

                    except Exception as e:
                        errores.append(f'Hoja {sheet_name}, Fila {index + 2}: Error procesando - {str(e)}')

                # Mostrar resultados de la hoja
                self.stdout.write(f'    📊 Hoja {sheet_name} completada:')
                self.stdout.write(f'      - Equipos procesados: {equipos_procesados}')
                self.stdout.write(f'      - Tipos creados: {tipos_creados}')
                self.stdout.write(f'      - Errores: {len(errores)}')

                # Si es dry-run, hacer rollback
                if dry_run:
                    transaction.set_rollback(True)
                    
                return equipos_procesados, tipos_creados, errores

        except Exception as e:
            return 0, 0, [f'Error procesando hoja {sheet_name}: {str(e)}']

    def generar_clave_tipo_equipo(self, descripcion):
        """
        Genera una clave de tipo de equipo basada en la descripción
        Intenta mapear a tipos existentes o crear uno nuevo
        """
        descripcion_lower = descripcion.lower()
        
        # Mapeo de palabras clave a tipos de equipo existentes
        mapeo_tipos = {
            'microscopio': 'microscopio_optico',
            'balanza': 'balanza_analitica',
            'espectrofotometro': 'espectrofotometro',
            'espectrofotómetro': 'espectrofotometro',
            'centrifuga': 'centrifuga',
            'centrífuga': 'centrifuga',
            'autoclave': 'autoclave',
            'incubadora': 'incubadora',
            'ph metro': 'ph_metro',
            'phmetro': 'ph_metro',
            'agitador': 'agitador_magnetico',
            'campana': 'campana_extractora',
            'mechero': 'mechero_bunsen',
            'bunsen': 'mechero_bunsen'
        }
        
        # Buscar coincidencias con tipos existentes
        for palabra_clave, tipo_equipo in mapeo_tipos.items():
            if palabra_clave in descripcion_lower:
                return tipo_equipo
        
        # Si no encuentra coincidencia, generar clave desde la descripción
        # Limpiar la descripción y crear clave
        descripcion_limpia = re.sub(r'[^\w\s]', '', descripcion_lower)
        palabras = descripcion_limpia.split()
        
        # Tomar las primeras 2-3 palabras más significativas
        palabras_filtradas = [p for p in palabras if len(p) > 2][:3]
        clave = '_'.join(palabras_filtradas)
        
        # Asegurar que la clave no sea muy larga
        if len(clave) > 50:
            clave = clave[:50]
        
        return clave

    def mostrar_estadisticas_tipos_equipo(self):
        """Muestra estadísticas de los tipos de equipo"""
        self.stdout.write(self.style.SUCCESS('\n📊 Estadísticas de Tipos de Equipo:'))
        
        for tipo_equipo in TipoEquipo.objects.all():
            total_equipos = tipo_equipo.equipos_individuales.count()
            operativos = tipo_equipo.equipos_individuales.filter(estado_operativo='operativo').count()
            
            self.stdout.write(f'  {tipo_equipo.get_nombre_display()}:')
            self.stdout.write(f'    Total: {total_equipos}')
            self.stdout.write(f'    Operativos: {operativos}')
