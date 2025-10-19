#!/usr/bin/env python
"""
Script para agregar logging temporal al formulario para debuggear
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from core.views import *

# Crear una versión temporal de la vista con logging extenso
def debug_form_submission():
    print("📋 CREAR LOGGING TEMPORAL EN VISTA")
    print("=" * 60)
    
    # Leer el archivo de vistas actual
    vista_path = '/Users/alvaroencinas/Desktop/centralizacion_laboratorios/core/views.py'
    
    # Encontrar la línea donde empieza agregar_datos_malla_view
    with open(vista_path, 'r') as f:
        lines = f.readlines()
    
    # Encontrar la línea de inicio de la función POST
    for i, line in enumerate(lines):
        if 'if request.method == \'POST\':' in line and 'agregar_datos_malla_view' in ''.join(lines[max(0, i-10):i]):
            print(f"   📍 Encontrada línea POST en línea {i+1}")
            
            # Insertar logging justo después del if request.method == 'POST':
            indent = '        '  # 8 espacios para mantener la indentación
            logging_code = f'''{indent}# 🚨 DEBUG TEMPORAL: Logging completo de datos recibidos
{indent}print("\\n" + "="*80)
{indent}print("🚨 DEBUGGING FORMULARIO - DATOS RECIBIDOS:")
{indent}print("="*80)
{indent}print(f"📊 Método: {{request.method}}")
{indent}print(f"👤 Usuario: {{request.user}}")
{indent}print(f"🌐 IP: {{request.META.get('REMOTE_ADDR', 'unknown')}}")
{indent}print("\\n📋 DATOS POST COMPLETOS:")
{indent}for key, value in request.POST.items():
{indent}    print(f"   {{key}}: '{{value}}'")
{indent}print("\\n" + "="*80)
{indent}
'''
            
            # Insertar el código de logging
            lines.insert(i + 2, logging_code)
            break
    
    # Escribir el archivo modificado
    with open(vista_path, 'w') as f:
        f.writelines(lines)
    
    print("   ✅ Logging temporal agregado")
    print("   📝 Ahora intente crear 'LABUBU 4' en el navegador")
    print("   🔍 Los datos aparecerán en la consola del servidor Django")

if __name__ == "__main__":
    debug_form_submission()