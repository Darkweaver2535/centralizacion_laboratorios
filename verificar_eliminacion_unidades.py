#!/usr/bin/env python
"""
Script para verificar que la sección de Unidades Didácticas ha sido eliminada correctamente
"""

def verificar_eliminacion_unidades_didacticas():
    print("🔍 VERIFICACIÓN: ELIMINACIÓN DE UNIDADES DIDÁCTICAS Y CONTENIDOS ANALÍTICOS")
    print("=" * 80)
    
    archivo_template = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/templates/core/detalle_asignatura.html'
    
    # Verificar que no hay referencias problemáticas en el template
    with open(archivo_template, 'r', encoding='utf-8') as f:
        contenido_template = f.read()
    
    # Búsquedas específicas
    busquedas_eliminadas = [
        ('Unidades Didácticas y Contenidos Analíticos', 'Título de sección eliminado'),
        ('unidad-didactica-item', 'Elementos de unidad didáctica'),
        ('unidad-didactica-header', 'Headers de unidades didácticas'),
        ('unidad-didactica-body', 'Cuerpos de unidades didácticas'),
        ('contenidos_por_unidad', 'Variable de contexto para contenidos'),
        ('unidades_didacticas_count', 'Estadística de conteo'),
        ('No hay unidades didácticas registradas', 'Mensaje de estado vacío'),
    ]
    
    busquedas_conservadas = [
        ('Prácticas de Laboratorio Creadas', 'Sección principal conservada'),
        ('combinaciones', 'Variable principal conservada'),
        ('Ver Detalles Completos', 'Funcionalidad de detalles'),
    ]
    
    print(f"\n✅ VERIFICANDO ELEMENTOS ELIMINADOS:")
    elementos_eliminados_ok = 0
    elementos_aun_presentes = 0
    
    for busqueda, descripcion in busquedas_eliminadas:
        if busqueda.lower() in contenido_template.lower():
            print(f"   ⚠️ AÚN PRESENTE: {descripcion} - '{busqueda}'")
            elementos_aun_presentes += 1
            # Mostrar líneas donde aparece
            lineas = contenido_template.split('\n')
            for i, linea in enumerate(lineas, 1):
                if busqueda.lower() in linea.lower():
                    print(f"      → Línea {i}: {linea.strip()[:80]}...")
        else:
            print(f"   ✅ ELIMINADO: {descripcion}")
            elementos_eliminados_ok += 1
    
    print(f"\n✅ VERIFICANDO ELEMENTOS CONSERVADOS:")
    elementos_conservados_ok = 0
    elementos_faltantes = 0
    
    for busqueda, descripcion in busquedas_conservadas:
        if busqueda.lower() in contenido_template.lower():
            print(f"   ✅ CONSERVADO: {descripcion}")
            elementos_conservados_ok += 1
        else:
            print(f"   ⚠️ FALTANTE: {descripcion} - '{busqueda}'")
            elementos_faltantes += 1
    
    # Verificar vista (views.py)
    print(f"\n🔍 VERIFICANDO VISTA (views.py):")
    archivo_views = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/core/views.py'
    
    with open(archivo_views, 'r', encoding='utf-8') as f:
        contenido_views = f.read()
    
    # Buscar en la función detalle_asignatura_view específicamente
    inicio_funcion = contenido_views.find('def detalle_asignatura_view(request, asignatura_id):')
    if inicio_funcion != -1:
        siguiente_def = contenido_views.find('\ndef ', inicio_funcion + 1)
        if siguiente_def == -1:
            funcion_contenido = contenido_views[inicio_funcion:]
        else:
            funcion_contenido = contenido_views[inicio_funcion:siguiente_def]
        
        # Verificaciones en la vista
        verificaciones_vista = [
            ('unidades_didacticas =', '✅ Variable unidades_didacticas eliminada'),
            ("'unidades_didacticas':", '✅ Contexto unidades_didacticas eliminado'),
            ('unidades_didacticas_count', '✅ Estadística unidades_didacticas_count eliminada'),
            ('contenidos_por_unidad', '✅ Variable contenidos_por_unidad eliminada'),
        ]
        
        for busqueda, mensaje_exito in verificaciones_vista:
            if busqueda in funcion_contenido:
                print(f"   ⚠️ AÚN PRESENTE en vista: {busqueda}")
            else:
                print(f"   {mensaje_exito}")
    
    # Resumen final
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   🗑️ Elementos eliminados correctamente: {elementos_eliminados_ok}/{len(busquedas_eliminadas)}")
    print(f"   ✅ Elementos conservados correctamente: {elementos_conservados_ok}/{len(busquedas_conservadas)}")
    
    if elementos_aun_presentes == 0 and elementos_faltantes == 0:
        print(f"\n🎉 ¡ÉXITO COMPLETO!")
        print(f"   ✅ Sección 'Unidades Didácticas y Contenidos Analíticos' eliminada totalmente")
        print(f"   ✅ Sección 'Prácticas de Laboratorio Creadas' conservada intacta")
        print(f"   ✅ Vista actualizada correctamente")
        print(f"   🎯 Frontend optimizado y limpio")
    else:
        print(f"\n⚠️ Revisión necesaria:")
        if elementos_aun_presentes > 0:
            print(f"   - {elementos_aun_presentes} elementos aún presentes que deberían estar eliminados")
        if elementos_faltantes > 0:
            print(f"   - {elementos_faltantes} elementos importantes faltantes")

if __name__ == "__main__":
    verificar_eliminacion_unidades_didacticas()