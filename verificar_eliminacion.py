#!/usr/bin/env python
"""
Script para verificar que la sección de Criterios de Desempeño ha sido eliminada
"""

def verificar_eliminacion_criterios():
    print("🔍 VERIFICANDO ELIMINACIÓN DE CRITERIOS DE DESEMPEÑO")
    print("=" * 60)
    
    archivo_template = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/templates/core/detalle_asignatura.html'
    
    # Verificar que no hay referencias a criterios en el template
    with open(archivo_template, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Búsquedas específicas
    busquedas = [
        ('Criterios de Desempeño', 'Títulos de sección'),
        ('criterio-item', 'Clases CSS de criterios'),
        ('criterio-nombre', 'Elementos de nombre de criterio'),
        ('criterio-descripcion', 'Elementos de descripción de criterio'),
        ('criterios_count', 'Estadística de criterios'),
        ('{% for criterio in criterios %}', 'Loop de criterios'),
        ('criterios de desempeño', 'Referencias en texto (minúsculas)'),
    ]
    
    encontrados = []
    eliminados_correctamente = []
    
    for busqueda, descripcion in busquedas:
        if busqueda.lower() in contenido.lower():
            encontrados.append((busqueda, descripcion))
        else:
            eliminados_correctamente.append((busqueda, descripcion))
    
    print(f"\n✅ ELEMENTOS ELIMINADOS CORRECTAMENTE ({len(eliminados_correctamente)}):")
    for busqueda, descripcion in eliminados_correctamente:
        print(f"   ✅ {descripcion}: '{busqueda}'")
    
    if encontrados:
        print(f"\n⚠️ ELEMENTOS AÚN PRESENTES ({len(encontrados)}):")
        for busqueda, descripcion in encontrados:
            print(f"   ⚠️ {descripcion}: '{busqueda}'")
            
            # Mostrar las líneas donde aparece
            lineas = contenido.split('\n')
            for i, linea in enumerate(lineas, 1):
                if busqueda.lower() in linea.lower():
                    print(f"      Línea {i}: {linea.strip()}")
    else:
        print(f"\n🎉 PERFECTO: Todos los elementos de Criterios de Desempeño han sido eliminados")
    
    # Verificar el archivo views.py
    print(f"\n🔍 VERIFICANDO VISTA (views.py):")
    archivo_views = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/core/views.py'
    
    with open(archivo_views, 'r', encoding='utf-8') as f:
        contenido_views = f.read()
    
    # Buscar en la función detalle_asignatura_view específicamente
    inicio_funcion = contenido_views.find('def detalle_asignatura_view(request, asignatura_id):')
    if inicio_funcion != -1:
        # Encontrar el final de la función (próxima función o final del archivo)
        siguiente_def = contenido_views.find('\ndef ', inicio_funcion + 1)
        if siguiente_def == -1:
            funcion_contenido = contenido_views[inicio_funcion:]
        else:
            funcion_contenido = contenido_views[inicio_funcion:siguiente_def]
        
        # Verificar que no hay referencias a criterios en la función
        if "'criterios':" in funcion_contenido or "criterios =" in funcion_contenido:
            print(f"   ⚠️ Aún hay referencias a criterios en detalle_asignatura_view")
        else:
            print(f"   ✅ Referencias a criterios eliminadas de detalle_asignatura_view")
        
        if "criterios_count" in funcion_contenido:
            print(f"   ⚠️ Aún hay referencias a criterios_count en asignatura_stats")
        else:
            print(f"   ✅ Estadística criterios_count eliminada correctamente")
    
    # Resumen final
    print(f"\n📊 RESUMEN FINAL:")
    if not encontrados and "criterios_count" not in funcion_contenido:
        print(f"   🎉 ¡ÉXITO COMPLETO! Sección de Criterios de Desempeño eliminada totalmente")
        print(f"   ✅ Template limpio")
        print(f"   ✅ Vista actualizada")
        print(f"   ✅ Estadísticas corregidas")
    else:
        print(f"   ⚠️ Eliminación parcial - revisar elementos pendientes")

if __name__ == "__main__":
    verificar_eliminacion_criterios()