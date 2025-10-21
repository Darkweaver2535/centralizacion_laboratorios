#!/usr/bin/env python3
"""
Script para corregir automáticamente la plantilla oficial de EMI
eliminando fragmentación XML en los tags de Jinja2
"""

import os
import zipfile
import re
from pathlib import Path
import shutil
from xml.etree import ElementTree as ET

def limpiar_tags_jinja2_xml(xml_content):
    """
    Limpia los tags de Jinja2 fragmentados en el XML de Word
    """
    # Patrones de fragmentación común en Word XML
    patterns = [
        # {{ variable_ name }} con espacios
        (r'\{\{\s*([^}]+?)\s*\}\}', r'{{\1}}'),
        
        # Tags fragmentados por elementos XML
        (r'\{\{([^}]*?)</w:t></w:r>(?:[^<]*<w:r[^>]*><w:rPr[^>]*>[^<]*</w:rPr><w:t[^>]*>)?([^}]*?)\}\}', r'{{\1\2}}'),
        
        # Espacios extra dentro de las variables
        (r'\{\{\s*(\w+)\s+(\w+)\s*\}\}', r'{{\1_\2}}'),
        
        # Triple braces
        (r'\{\{\{([^}]+)\}\}\}', r'{{\1}}'),
        
        # Espacios alrededor de underscores
        (r'\{\{\s*(\w+)\s*_\s*(\w+)\s*\}\}', r'{{\1_\2}}'),
    ]
    
    content = xml_content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def corregir_plantilla_emi(plantilla_original, plantilla_corregida):
    """
    Corrige la plantilla oficial de EMI limpiando los tags de Jinja2
    """
    print(f"🔧 Corrigiendo plantilla EMI...")
    print(f"   Origen: {plantilla_original}")
    print(f"   Destino: {plantilla_corregida}")
    
    if not os.path.exists(plantilla_original):
        print(f"❌ Error: No se encontró la plantilla original en {plantilla_original}")
        return False
    
    # Crear directorio de destino si no existe
    os.makedirs(os.path.dirname(plantilla_corregida), exist_ok=True)
    
    # Copiar el archivo original como base
    shutil.copy2(plantilla_original, plantilla_corregida)
    
    try:
        # Abrir el archivo Word como ZIP
        with zipfile.ZipFile(plantilla_corregida, 'r') as zip_read:
            # Crear archivo temporal
            temp_path = plantilla_corregida + '.temp'
            
            with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_write:
                
                for item in zip_read.infolist():
                    content = zip_read.read(item.filename)
                    
                    # Si es un archivo XML, limpiar los tags de Jinja2
                    if item.filename.endswith('.xml'):
                        try:
                            content_str = content.decode('utf-8')
                            
                            # Aplicar correcciones específicas
                            corrections = [
                                # Correcciones específicas encontradas en el análisis
                                (r'\{\{\s*parte\s*_\s*indice\s*\}\}', '{{parte_indice}}'),
                                (r'\{\{\s*cantidad\s*_\s*reactivo(\d+)\s*\}\}', r'{{cantidad_reactivo\1}}'),
                                (r'\{\{\s*codigo\s*_\s*de\s*_\s*documento\s*\}\}', '{{codigo_de_documento}}'),
                                (r'\{\{\s*versio\s*_\s*de\s*_\s*documento\s*\}\}', '{{version_de_documento}}'),
                                (r'\{\{\s*pagina\s*\}\}', '{{pagina}}'),
                                
                                # Patrones generales de limpieza
                                (r'\{\{\{([^}]+)\}\}\}', r'{{\1}}'),  # Triple braces
                                (r'\{\{\s+([^}]+?)\s+\}\}', r'{{\1}}'),  # Espacios extras
                                (r'\{\{\s*([^}]+?)\s*\}\}', r'{{\1}}'),  # Espacios alrededor
                            ]
                            
                            content_cleaned = content_str
                            for pattern, replacement in corrections:
                                content_cleaned = re.sub(pattern, replacement, content_cleaned, flags=re.IGNORECASE)
                            
                            # Limpiar fragmentación XML más compleja
                            content_cleaned = limpiar_tags_jinja2_xml(content_cleaned)
                            
                            content = content_cleaned.encode('utf-8')
                            
                        except UnicodeDecodeError:
                            # Si no se puede decodificar, mantener contenido original
                            pass
                    
                    zip_write.writestr(item, content)
        
        # Reemplazar archivo original con el corregido
        os.replace(temp_path, plantilla_corregida)
        
        print(f"✅ Plantilla corregida exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error corrigiendo plantilla: {e}")
        # Limpiar archivos temporales
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def verificar_plantilla_corregida(plantilla_path):
    """
    Verifica que la plantilla corregida tenga tags de Jinja2 válidos
    """
    print(f"\n🔍 Verificando plantilla corregida...")
    
    try:
        with zipfile.ZipFile(plantilla_path, 'r') as zip_file:
            problemas_encontrados = 0
            
            for xml_file in zip_file.namelist():
                if xml_file.endswith('.xml'):
                    content = zip_file.read(xml_file).decode('utf-8', errors='ignore')
                    
                    # Buscar tags problemáticos
                    problematic_patterns = [
                        r'\{\{\{[^}]+\}\}\}',  # Triple braces
                        r'\{\{\s+[^}]+\s+\}\}',  # Espacios en medio
                        r'\{\{\s*\w+\s+\w+\s*\}\}',  # Palabras separadas por espacio
                    ]
                    
                    for pattern in problematic_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            print(f"⚠️  Tags problemáticos en {xml_file}:")
                            for match in matches[:5]:  # Mostrar solo primeros 5
                                print(f"     {match}")
                            problemas_encontrados += len(matches)
            
            if problemas_encontrados == 0:
                print(f"✅ Plantilla verificada: No se encontraron problemas")
                return True
            else:
                print(f"❌ Se encontraron {problemas_encontrados} tags problemáticos")
                return False
                
    except Exception as e:
        print(f"❌ Error verificando plantilla: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 CORRECTOR AUTOMÁTICO DE PLANTILLA EMI")
    print("=" * 50)
    
    # Rutas
    plantilla_original = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/pruebas/FORMATO GUÍA DE LABORATORIO.docx"
    plantilla_corregida = "/Users/alvaroencinas/Desktop/centralizacion_laboratorios/templates/core/plantilla_guia_laboratorio_emi_corregida.docx"
    
    # Corregir plantilla
    if corregir_plantilla_emi(plantilla_original, plantilla_corregida):
        
        # Verificar corrección
        if verificar_plantilla_corregida(plantilla_corregida):
            print(f"\n🎉 ¡PLANTILLA EMI CORREGIDA EXITOSAMENTE!")
            print(f"📁 Ubicación: {plantilla_corregida}")
            
            # Actualizar el sistema para usar la plantilla corregida
            print(f"\n🔄 Para usar esta plantilla, ejecutar:")
            print(f"   1. Actualizar guias/plantilla_utils.py")
            print(f"   2. Cambiar ruta a: plantilla_guia_laboratorio_emi_corregida.docx")
            print(f"   3. Probar generación de documentos")
            
        else:
            print(f"\n⚠️  La plantilla fue parcialmente corregida pero aún tiene problemas")
            print(f"💡 Recomendación: Corregir manualmente los tags restantes")
    else:
        print(f"\n❌ No se pudo corregir la plantilla automáticamente")
        print(f"💡 Recomendación: Seguir las instrucciones manuales")

if __name__ == "__main__":
    main()