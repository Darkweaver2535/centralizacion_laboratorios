#!/usr/bin/env python3
"""
Script mejorado para importar equipos desde Excel con manejo completo de los 22 campos requeridos
Mapea datos del Excel a los campos del sistema y completa campos faltantes con valores por defecto
"""

import os
import sys
import django
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.db import transaction
from core.models import UnidadAcademica, Carrera, Asignatura, UnidadTematica, GuiaLaboratorio, Practica, Laboratorio
from usuarios.models import Usuario
from equipos.models import Equipo

class ImportadorExcelMejorado:
    """Importador mejorado que maneja todos los 22 campos requeridos"""
    
    def __init__(self, archivo_excel):
        self.archivo_excel = archivo_excel
        self.df = None
        self.errores = []
        self.exitosos = []
        
        # Mapeo de estados
        self.mapeo_estados = {
            'OPERATIVO': 'operativo',
            'OPERATIVO.': 'operativo', 
            'BUENO': 'operativo',
            'REGULAR': 'necesita_mantenimiento',
            'MALO': 'fuera_servicio',
            'FUERA DE SERVICIO': 'fuera_servicio',
            'EN MANTENIMIENTO': 'necesita_mantenimiento',
            'DAÑADO': 'fuera_servicio',
            'OBSOLETO': 'obsoleto',
            'NECESITA MANTENIMIENTO': 'necesita_mantenimiento',
        }
        
        # Mapeo de unidades académicas
        self.mapeo_unidades = {
            'UALP': 'UALP',
            'LA PAZ': 'UALP',
            'UACB': 'UACB', 
            'COCHABAMBA': 'UACB',
            'UASC': 'UASC',
            'SANTA CRUZ': 'UASC',
            'UATP': 'UATP',
            'TROPICO': 'UATP',
            'UCRB': 'UCRB',
            'RIBERALTA': 'UCRB',
        }
        
        # Cache para objetos reutilizables
        self._cache_objetos = {}
    
    def validar_archivo(self):
        """Validar archivo Excel"""
        try:
            if not os.path.exists(self.archivo_excel):
                raise FileNotFoundError(f"Archivo no encontrado: {self.archivo_excel}")
            
            self.df = pd.read_excel(self.archivo_excel)
            
            # Verificar columnas mínimas del Excel
            columnas_requeridas = [
                'N', 'UNIDAD ACADEMICA', 'RESPONSABLE', 'DESCRIPCION DEL ACTIVO', 'ESTADO'
            ]
            
            columnas_faltantes = [col for col in columnas_requeridas if col not in self.df.columns]
            
            if columnas_faltantes:
                raise ValueError(f"Faltan columnas: {', '.join(columnas_faltantes)}")
            
            print(f"✅ Archivo validado: {len(self.df)} filas")
            return True
            
        except Exception as e:
            print(f"❌ Error al validar archivo: {e}")
            return False
    
    def limpiar_datos(self):
        """Limpiar datos del Excel"""
        try:
            self.df = self.df.fillna('')
            
            # Limpiar columnas de texto
            for col in ['UNIDAD ACADEMICA', 'RESPONSABLE', 'DESCRIPCION DEL ACTIVO', 'ESTADO', 'CODIGO']:
                if col in self.df.columns:
                    self.df[col] = self.df[col].astype(str).str.strip().str.upper()
            
            # Limpiar C.I.
            if 'C.I.' in self.df.columns:
                self.df['C.I.'] = self.df['C.I.'].astype(str).str.replace(r'\D', '', regex=True)
            
            print("✅ Datos limpiados")
            return True
            
        except Exception as e:
            print(f"❌ Error al limpiar datos: {e}")
            return False
    
    def crear_objetos_por_defecto(self):
        """Crear objetos por defecto necesarios para los equipos"""
        try:
            print("🔧 Creando objetos por defecto...")
            
            # 1. Unidad Temática por defecto
            # Necesitamos una asignatura para crear la unidad temática
            asignatura_default = Asignatura.objects.first()
            if not asignatura_default:
                raise ValueError("No hay asignaturas en el sistema")
            
            unidad_tematica, created = UnidadTematica.objects.get_or_create(
                nombre="Equipos Importados desde Excel",
                asignatura=asignatura_default,
                numero=999,
                defaults={
                    'descripcion': 'Unidad temática temporal para equipos importados desde Excel'
                }
            )
            if created:
                print(f"  ✅ Unidad temática creada: {unidad_tematica.nombre}")
            self._cache_objetos['unidad_tematica'] = unidad_tematica
            
            # 2. Guía de Laboratorio por defecto
            guia_laboratorio, created = GuiaLaboratorio.objects.get_or_create(
                nombre="Guía para Equipos Importados",
                unidad_tematica=unidad_tematica,
                numero=999,
                defaults={
                    'descripcion': 'Guía temporal para equipos importados desde Excel'
                }
            )
            if created:
                print(f"  ✅ Guía de laboratorio creada: {guia_laboratorio.nombre}")
            self._cache_objetos['guia_laboratorio'] = guia_laboratorio
            
            # 3. Práctica por defecto
            practica, created = Practica.objects.get_or_create(
                nombre="Práctica con Equipos Importados",
                guia_laboratorio=guia_laboratorio,
                numero=999,
                defaults={
                    'descripcion': 'Práctica temporal para equipos importados desde Excel'
                }
            )
            if created:
                print(f"  ✅ Práctica creada: {practica.nombre}")
            self._cache_objetos['practica'] = practica
            
            # 4. Asignatura por defecto - ya está guardada en cache
            self._cache_objetos['asignatura'] = asignatura_default
            
            print("✅ Objetos por defecto creados/verificados")
            return True
            
        except Exception as e:
            print(f"❌ Error al crear objetos por defecto: {e}")
            return False
    
    def obtener_unidad_academica(self, nombre_excel):
        """Obtener unidad académica"""
        try:
            nombre_norm = str(nombre_excel).strip().upper()
            codigo = self.mapeo_unidades.get(nombre_norm)
            
            if not codigo:
                for excel_name, db_code in self.mapeo_unidades.items():
                    if excel_name in nombre_norm:
                        codigo = db_code
                        break
            
            if codigo:
                ua = UnidadAcademica.objects.get(nombre=codigo)
                return ua
            else:
                raise ValueError(f"Unidad académica no mapeada: {nombre_excel}")
                
        except UnidadAcademica.DoesNotExist:
            raise ValueError(f"Unidad académica no existe: {codigo}")
    
    def obtener_carrera_por_defecto(self, unidad_academica):
        """Obtener primera carrera disponible para la unidad académica"""
        carrera = Carrera.objects.filter(unidad_academica=unidad_academica).first()
        if not carrera:
            raise ValueError(f"No hay carreras para {unidad_academica}")
        return carrera
    
    def obtener_laboratorio(self, unidad_academica):
        """Obtener o crear laboratorio por defecto"""
        cache_key = f"laboratorio_{unidad_academica.nombre}"
        
        if cache_key not in self._cache_objetos:
            laboratorio, created = Laboratorio.objects.get_or_create(
                nombre=f"Laboratorio {unidad_academica.nombre}",
                defaults={
                    'descripcion': f'Laboratorio de equipos importados para {unidad_academica.nombre}',
                    'ubicacion': f'Edificio {unidad_academica.nombre}',
                    'capacidad': 20,
                    'responsable': 'Por asignar',
                    'seccion_area': 'Equipos Importados',
                    'identificador_aula': f'LAB-{unidad_academica.nombre}'
                }
            )
            if created:
                print(f"  ✅ Laboratorio creado: {laboratorio.nombre}")
            self._cache_objetos[cache_key] = laboratorio
        
        return self._cache_objetos[cache_key]
    
    def obtener_usuario_responsable(self, nombre, ci, cargo, oficina, unidad_academica):
        """Obtener o crear usuario responsable"""
        try:
            # Buscar por C.I. primero
            if ci and len(str(ci).strip()) >= 6:
                ci_limpio = str(ci).strip()
                try:
                    return Usuario.objects.get(numero_documento=ci_limpio)
                except Usuario.DoesNotExist:
                    pass
            
            # Crear nuevo usuario
            if not nombre or nombre.strip() == '':
                nombre = "Usuario Importado"
            
            # Generar username único
            nombre_base = nombre.replace(' ', '').lower()[:10]
            username = nombre_base
            contador = 1
            
            while Usuario.objects.filter(username=username).exists():
                username = f"{nombre_base}{contador}"
                contador += 1
            
            # Crear usuario temporal
            usuario = Usuario.objects.create_user(
                username=username,
                correo_institucional=f"{username}@temp.emi.edu.bo",
                email=f"{username}@temp.emi.edu.bo",
                first_name=nombre.title(),
                numero_documento=str(ci).strip() if ci else '',
                rol='auxiliar',
                unidad=unidad_academica.nombre,  # Usar unidad en lugar de unidad_academica
                cargo_posicion=cargo.title() if cargo else 'Responsable de Equipo',  # Usar cargo_posicion
                sede_asignacion=oficina.title() if oficina else '-',
                estado_usuario='activo',
                debe_cambiar_password=True
            )
            
            return usuario
            
        except Exception as e:
            raise ValueError(f"Error al crear usuario: {e}")
    
    def normalizar_estado(self, estado_excel):
        """Normalizar estado del Excel"""
        estado_norm = str(estado_excel).strip().upper()
        return self.mapeo_estados.get(estado_norm, 'operativo')
    
    def procesar_fila(self, fila, numero_fila):
        """Procesar una fila del Excel creando un equipo completo"""
        try:
            # Extraer datos del Excel
            numero = fila.get('N', numero_fila)
            unidad_academica_str = fila.get('UNIDAD ACADEMICA', '')
            responsable = fila.get('RESPONSABLE', '')
            ci = fila.get('C.I.', '')
            cargo = fila.get('CARGO', '')
            oficina = fila.get('OFICINA', '')
            codigo_excel = fila.get('CODIGO', '')
            descripcion = fila.get('DESCRIPCION DEL ACTIVO', '')
            estado_str = fila.get('ESTADO', '')
            fecha_asignacion = fila.get('FECHA DE ASIGNACION', None)
            
            # Validaciones mínimas
            if not descripcion or descripcion.strip() == '':
                raise ValueError("Descripción del activo requerida")
            
            if not unidad_academica_str or unidad_academica_str.strip() == '':
                raise ValueError("Unidad académica requerida")
            
            # Obtener objetos del sistema
            unidad_academica = self.obtener_unidad_academica(unidad_academica_str)
            carrera = self.obtener_carrera_por_defecto(unidad_academica)
            laboratorio = self.obtener_laboratorio(unidad_academica)
            usuario_responsable = self.obtener_usuario_responsable(
                responsable, ci, cargo, oficina, unidad_academica
            )
            estado_normalizado = self.normalizar_estado(estado_str)
            
            # Generar código de inventario único
            if codigo_excel and codigo_excel.strip():
                codigo_inventario = codigo_excel.strip()
            else:
                contador = Equipo.objects.count() + numero_fila
                codigo_inventario = f"{unidad_academica.nombre}-IMP-{contador:06d}"
            
            # Asegurar unicidad del código
            base_codigo = codigo_inventario
            contador = 1
            while Equipo.objects.filter(codigo_inventario=codigo_inventario).exists():
                codigo_inventario = f"{base_codigo}-{contador}"
                contador += 1
            
            # Crear equipo con TODOS los 22 campos requeridos
            equipo_data = {
                # 1. UNIDAD ACADÉMICA
                'unidad_academica': unidad_academica,
                
                # 2. CARRERA (por defecto)
                'carrera': carrera,
                
                # 3. SEMESTRE (por defecto)
                'semestre': 1,
                
                # 4. ASIGNATURA (por defecto)
                'asignatura': self._cache_objetos['asignatura'],
                
                # 5. CARGA HORARIA SEMANAL (por defecto)
                'carga_horaria_semanal': 2,
                
                # 6. CARGA HORARIA SEMESTRAL (por defecto)
                'carga_horaria_semestral': 32,
                
                # 7. UNIDAD TEMÁTICA (por defecto)
                'unidad_tematica': self._cache_objetos['unidad_tematica'],
                
                # 8. GUÍA DE LABORATORIO (por defecto)
                'guia_laboratorio': self._cache_objetos['guia_laboratorio'],
                
                # 9. PRÁCTICA (por defecto)
                'practica': self._cache_objetos['practica'],
                
                # 10. EQUIPO EXISTENTE (del Excel)
                'equipo_existente': descripcion[:200],
                
                # 11. MARCA (por defecto, editable)
                'marca': '-',
                
                # 12. MODELO (por defecto, editable)
                'modelo': '-',
                
                # 13. ESTADO (del Excel)
                'estado': estado_normalizado,
                
                # 14. NÚMERO DE UNIDADES DEL EQUIPO (por defecto)
                'numero_unidades': 1,
                
                # 15. ES UN ACTIVO FIJO (por defecto)
                'es_activo_fijo': True,
                
                # 16. FOTOGRAFÍA FRONTAL DEL EQUIPO (vacío, editable)
                'fotografia_frontal': None,
                
                # 17. FOTOGRAFÍA DE LA PLACA (vacío, editable)
                'fotografia_placa': None,
                
                # 18. UBICACIÓN DEL EQUIPO (laboratorio por defecto)
                'laboratorio': laboratorio,
                
                # 19. SECCIÓN/ÁREA (del Excel si existe, sino por defecto)
                'seccion_area': oficina[:100] if oficina else '-',
                
                # 20. IDENTIFICADOR/Nº DE AULA (por defecto, editable)
                'identificador_aula': '-',
                
                # 21. EQUIPO REQUERIDO (por defecto, editable)
                'equipo_requerido': '-',
                
                # 22. NÚMERO DE EQUIPOS REQUERIDOS (por defecto)
                'numero_equipos_requeridos': 0,
                
                # Campos adicionales
                'usuario_creador': usuario_responsable,
                'codigo_inventario': codigo_inventario,
                'observaciones': f"""
DATOS IMPORTADOS DESDE EXCEL:
- N°: {numero}
- Responsable: {responsable}
- C.I.: {ci}
- Cargo: {cargo}
- Oficina: {oficina}
- Código original: {codigo_excel}
- Estado original: {estado_str}
- Fecha asignación: {fecha_asignacion}

NOTA: Los campos marcados con "-" pueden editarse posteriormente.
Campos por defecto creados automáticamente durante la importación.
                """.strip()
            }
            
            # Crear el equipo
            equipo = Equipo.objects.create(**equipo_data)
            
            return {
                'exito': True,
                'equipo': equipo,
                'codigo': codigo_inventario,
                'descripcion': descripcion[:50] + '...' if len(descripcion) > 50 else descripcion,
                'responsable': responsable[:30] + '...' if len(responsable) > 30 else responsable
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'fila': numero_fila,
                'descripcion': descripcion[:50] if 'descripcion' in locals() else 'N/A'
            }
    
    def importar_datos(self):
        """Importar todos los datos"""
        print(f"\n🚀 Iniciando importación de {len(self.df)} equipos...")
        print("📋 Cada equipo tendrá los 22 campos requeridos para aparecer en la tabla general")
        print("🔧 Campos faltantes se llenarán con '-' y podrán editarse posteriormente\n")
        
        with transaction.atomic():
            for index, fila in self.df.iterrows():
                resultado = self.procesar_fila(fila, index + 1)
                
                if resultado['exito']:
                    self.exitosos.append(resultado)
                    print(f"✅ {index+1:3d}: {resultado['descripcion']} | {resultado['responsable']}")
                else:
                    self.errores.append(resultado)
                    print(f"❌ {index+1:3d}: {resultado['error']}")
        
        # Resumen final
        print(f"\n" + "="*60)
        print(f"📊 RESUMEN DE IMPORTACIÓN")
        print(f"="*60)
        print(f"✅ Equipos importados exitosamente: {len(self.exitosos)}")
        print(f"❌ Errores encontrados: {len(self.errores)}")
        print(f"📋 Total procesados: {len(self.exitosos) + len(self.errores)}")
        
        if self.exitosos:
            print(f"\n🎉 Los {len(self.exitosos)} equipos ya están disponibles en:")
            print(f"   📍 http://127.0.0.1:8000/equipos/ (Lista completa)")
            print(f"   📍 http://127.0.0.1:8000/visualizacion/ (Con filtros)")
            print(f"   📍 Dashboard principal para estadísticas")
        
        if self.errores:
            print(f"\n🔍 ERRORES DETALLADOS:")
            for error in self.errores[:10]:  # Mostrar solo primeros 10
                print(f"   - Fila {error['fila']}: {error['error']}")
            if len(self.errores) > 10:
                print(f"   ... y {len(self.errores) - 10} errores más")
        
        return len(self.exitosos), len(self.errores)

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Importar equipos desde Excel (versión completa)')
    parser.add_argument('archivo', help='Ruta al archivo Excel')
    parser.add_argument('--test', action='store_true', help='Modo prueba (no guarda)')
    
    args = parser.parse_args()
    
    try:
        importador = ImportadorExcelMejorado(args.archivo)
        
        # Validar archivo
        if not importador.validar_archivo():
            return 1
        
        # Limpiar datos
        if not importador.limpiar_datos():
            return 1
        
        # Crear objetos por defecto
        if not importador.crear_objetos_por_defecto():
            return 1
        
        if args.test:
            print(f"\n🧪 MODO DE PRUEBA - No se guardarán cambios")
            print(f"📋 Se procesarían {len(importador.df)} equipos")
            return 0
        
        # Confirmar importación
        print(f"\n📋 Vista previa (primeras 3 filas):")
        print(importador.df.head(3)[['UNIDAD ACADEMICA', 'RESPONSABLE', 'DESCRIPCION DEL ACTIVO', 'ESTADO']].to_string())
        
        respuesta = input(f"\n¿Importar {len(importador.df)} equipos? (s/N): ")
        if respuesta.lower() != 's':
            print("❌ Importación cancelada")
            return 0
        
        # Importar
        exitosos, errores = importador.importar_datos()
        
        if exitosos > 0:
            print(f"\n🎉 ¡Importación completada! {exitosos} equipos disponibles en el sistema")
            return 0
        else:
            print(f"\n❌ No se pudieron importar equipos")
            return 1
    
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
