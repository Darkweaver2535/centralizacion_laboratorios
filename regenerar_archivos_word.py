#!/usr/bin/env python
"""
Script para regenerar los archivos Word de las guías existentes.
Úsalo si los archivos actuales están corruptos.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from guias.models import GuiaGenerada
from guias.views import generar_documento_word
from django.core.files.base import ContentFile
from datetime import datetime

def regenerar_archivos():
    """Regenera los archivos Word de todas las guías"""
    
    print("=" * 80)
    print("REGENERACIÓN DE ARCHIVOS WORD")
    print("=" * 80)
    
    guias = GuiaGenerada.objects.all()
    total = guias.count()
    
    if total == 0:
        print("\n❌ No se encontraron guías en la base de datos")
        return
    
    print(f"\n📋 Se encontraron {total} guías")
    print("\n🔄 Iniciando regeneración...\n")
    
    exitosos = 0
    fallidos = 0
    
    for i, guia in enumerate(guias, 1):
        print(f"[{i}/{total}] Procesando: '{guia.titulo}'")
        
        try:
            # Generar el documento
            word_buffer = generar_documento_word(guia)
            
            if word_buffer is None:
                print(f"   ❌ Error: La generación retornó None")
                fallidos += 1
                continue
            
            # Verificar que tenga contenido
            buffer_size = word_buffer.getbuffer().nbytes
            if buffer_size == 0:
                print(f"   ❌ Error: El documento está vacío")
                fallidos += 1
                continue
            
            # Guardar el archivo
            filename = f'guia_{guia.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
            guia.archivo_word.save(
                filename,
                ContentFile(word_buffer.getvalue()),
                save=True
            )
            
            print(f"   ✅ Archivo generado: {filename} ({buffer_size:,} bytes)")
            exitosos += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            fallidos += 1
    
    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)
    print(f"Total procesadas: {total}")
    print(f"✅ Exitosas: {exitosos}")
    print(f"❌ Fallidas: {fallidos}")
    print("=" * 80)

if __name__ == '__main__':
    respuesta = input("\n⚠️  Esto regenerará TODOS los archivos Word. ¿Continuar? (s/n): ")
    if respuesta.lower() == 's':
        regenerar_archivos()
    else:
        print("Operación cancelada")
