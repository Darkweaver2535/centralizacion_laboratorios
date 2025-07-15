"""
Script de depuración para verificar coincidencia entre vista y Excel
"""

from visualizacion.views import obtener_datos_general_completos
from ingreso_datos.models import *
import json

def debug_vista_vs_excel():
    """Compara los datos de la vista con los del Excel"""
    
    # Test con todos los datos
    filtros = {
        'unidad_academica': None,
        'semestre': None,
        'carrera': None,
        'materia': None,
        'laboratorio': None,
        'tipo_equipo': None
    }
    
    # Obtener datos Excel
    datos_excel = obtener_datos_general_completos(filtros)
    
    print("=== DEPURACIÓN VISTA VS EXCEL ===")
    print(f"Total registros en Excel: {len(datos_excel)}")
    
    # Simular exactamente lo que hace la vista filtrar_datos
    laboratorios = Laboratorio.objects.all()
    
    # Contadores separados como en la vista
    datos_laboratorios = []
    datos_ensayos = []
    datos_equipos = []
    
    for laboratorio in laboratorios:
        # Datos del laboratorio
        datos_laboratorios.append({
            'unidad_academica': laboratorio.unidad_academica.get_nombre_display(),
            'laboratorio': laboratorio.get_nombre_display(),
        })
        
        # Datos de ensayos
        for ensayo in laboratorio.ensayos.all():
            datos_ensayos.append({
                'laboratorio': laboratorio.get_nombre_display(),
                'ensayo': ensayo.get_nombre_display(),
            })
            
            # Datos de equipos
            for equipo in ensayo.equipos.all():
                equipos_seleccionados = equipo.equipos_seleccionados.all()
                
                if equipos_seleccionados:
                    for equipo_individual in equipos_seleccionados:
                        datos_equipos.append({
                            'laboratorio': laboratorio.get_nombre_display(),
                            'ensayo': ensayo.get_nombre_display(),
                            'codigo_equipo': equipo_individual.codigo,
                        })
                else:
                    datos_equipos.append({
                        'laboratorio': laboratorio.get_nombre_display(),
                        'ensayo': ensayo.get_nombre_display(),
                        'codigo_equipo': 'Sin especificar',
                    })
    
    print(f"\nDatos de la vista:")
    print(f"  - Laboratorios: {len(datos_laboratorios)}")
    print(f"  - Ensayos: {len(datos_ensayos)}")
    print(f"  - Equipos: {len(datos_equipos)}")
    
    # En la vista, la tabla general se construye combinando estos datos
    # Vamos a simular esa lógica
    print(f"\nLa vista web muestra:")
    print(f"  - Pestaña Laboratorios: {len(datos_laboratorios)} filas")
    print(f"  - Pestaña Ensayos: {len(datos_ensayos)} filas")
    print(f"  - Pestaña Equipos: {len(datos_equipos)} filas")
    
    # La pestaña General combina todo
    print(f"  - Pestaña General: Se construye dinámicamente con JavaScript")
    
    # Analizar los datos de Excel
    print(f"\nAnálisis de datos Excel:")
    tipos_registro = {}
    for dato in datos_excel:
        if dato['ensayo'] == '-':
            tipo = 'laboratorio_sin_ensayos'
        elif dato['codigo_equipo'] == '-':
            tipo = 'ensayo_sin_equipos'
        elif dato['codigo_equipo'] == 'Sin especificar':
            tipo = 'tipo_equipo_sin_individuales'
        else:
            tipo = 'equipo_individual'
        
        tipos_registro[tipo] = tipos_registro.get(tipo, 0) + 1
    
    for tipo, cantidad in tipos_registro.items():
        print(f"  - {tipo}: {cantidad}")
    
    # Mostrar todos los registros de Excel
    print(f"\nTodos los registros de Excel:")
    for i, registro in enumerate(datos_excel, 1):
        print(f"  {i}. {registro['unidad_academica']} | {registro['laboratorio']} | {registro['ensayo']} | {registro['codigo_equipo']}")

if __name__ == "__main__":
    debug_vista_vs_excel()
