#!/usr/bin/env python3
"""
Corrector específico para la plantilla EMI manual del usuario
"""

import os
import zipfile
import re
import shutil

def corregir_tag_especifico(plantilla_path):
    """
    Corrige el tag específico problemático en la plantilla EMI manual
    """
    print(f"🔧 Corrigiendo tag específico en: {plantilla_path}")
    
    # Crear backup
    backup_path = plantilla_path + '.backup'
    shutil.copy2(plantilla_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    
    try:
        # Crear archivo temporal
        temp_path = plantilla_path + '.temp'
        
        with zipfile.ZipFile(plantilla_path, 'r') as zip_read:
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                
                for item in zip_read.infolist():
                    content = zip_read.read(item.filename)
                    
                    # Si es XML, corregir el tag problemático
                    if item.filename.endswith('.xml'):
                        try:
                            content_str = content.decode('utf-8')
                            
                            # Correcciones específicas encontradas
                            corrections = [
                                # El problema principal encontrado
                                (r'\{\{\s*cantidad\s*_\s*reactivo1\s*\}\}', '{{cantidad_reactivo1}}'),
                                
                                # Otros patrones problemáticos posibles
                                (r'\{\{\s*cantidad\s*_\s*reactivo(\d+)\s*\}\}', r'{{cantidad_reactivo\1}}'),
                                (r'\{\{\s*cantidad\s*_\s*material(\d+)\s*\}\}', r'{{cantidad_material\1}}'),
                                (r'\{\{\s*cantidad\s*_\s*equipo(\d+)\s*\}\}', r'{{cantidad_equipo\1}}'),
                                (r'\{\{\s*cantidad\s*_\s*herramienta(\d+)\s*\}\}', r'{{cantidad_herramienta\1}}'),
                                
                                # Limpiar espacios extra en general
                                (r'\{\{\s+([^}]+?)\s+\}\}', r'{{\1}}'),
                                (r'\{\{\s*([^}]+?)\s*\}\}', r'{{\1}}'),
                            ]
                            
                            content_cleaned = content_str
                            changes_made = 0
                            
                            for pattern, replacement in corrections:
                                old_content = content_cleaned
                                content_cleaned = re.sub(pattern, replacement, content_cleaned, flags=re.IGNORECASE)
                                if old_content != content_cleaned:
                                    changes_made += 1
                            
                            if changes_made > 0:
                                print(f"✅ Corregido {changes_made} problemas en {item.filename}")
                            
                            content = content_cleaned.encode('utf-8')
                            
                        except UnicodeDecodeError:
                            # Si no se puede decodificar, mantener contenido original
                            pass
                    
                    zip_write.writestr(item, content)
        
        # Reemplazar archivo original
        os.replace(temp_path, plantilla_path)
        
        print(f"✅ Plantilla corregida exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo plantilla: {e}")
        # Restaurar backup si hay error
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, plantilla_path)
            print(f"✅ Backup restaurado")
        return False

def verificar_correccion(plantilla_path):
    """
    Verifica que la corrección haya funcionado
    """
    print(f"\n🔍 Verificando corrección...")
    
    try:
        with zipfile.ZipFile(plantilla_path, 'r') as zip_file:
            problemas_encontrados = 0
            
            for xml_file in zip_file.namelist():
                if xml_file.endswith('.xml'):
                    content = zip_file.read(xml_file).decode('utf-8', errors='ignore')
                    
                    # Buscar patrones problemáticos específicos
                    problematic_patterns = [
                        r'\{\{\s*cantidad\s*_\s*reactivo1\s*\}\}',  # El problema principal
                        r'\{\{\s+[^}]+\s+\}\}',  # Espacios dobles
                        r'\{\{\{[^}]+\}\}\}',    # Triple braces
                    ]
                    
                    for pattern in problematic_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"⚠️  Problema restante en {xml_file}:")
                            for match in matches[:3]:
                                print(f"     {match}")
                            problemas_encontrados += len(matches)
            
            if problemas_encontrados == 0:
                print(f"✅ Verificación exitosa: No se encontraron problemas")
                return True
            else:
                print(f"❌ Se encontraron {problemas_encontrados} problemas restantes")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 CORRECTOR ESPECÍFICO PARA PLANTILLA EMI MANUAL")
    print("=" * 55)
    
    plantilla_path = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/templates/core/plantilla_emi_manual.docx"
    
    if not os.path.exists(plantilla_path):
        print(f"❌ Error: No se encontró la plantilla en {plantilla_path}")
        return
    
    # Corregir plantilla
    if corregir_tag_especifico(plantilla_path):
        # Verificar corrección
        if verificar_correccion(plantilla_path):
            print(f"\n🎉 ¡PLANTILLA EMI MANUAL CORREGIDA EXITOSAMENTE!")
            print(f"📁 Ubicación: {plantilla_path}")
            print(f"🔄 Ahora puedes probar la generación de documentos")
        else:
            print(f"\n⚠️  Corrección parcial - revisar problemas restantes")
    else:
        print(f"\n❌ No se pudo corregir la plantilla")

if __name__ == "__main__":
    main()