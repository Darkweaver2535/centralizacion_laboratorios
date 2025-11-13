#!/usr/bin/env python
"""
Script para probar la generación de documentos Word y diagnosticar problemas.
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from guias.models import GuiaGenerada
from guias.views import generar_documento_word

def test_word_generation():
    """Prueba la generación de documentos Word"""
    
    print("=" * 80)
    print("TEST DE GENERACIÓN DE DOCUMENTOS WORD")
    print("=" * 80)
    
    # Obtener la última guía generada
    try:
        guia = GuiaGenerada.objects.latest('created_at')
        print(f"\n✅ Guía encontrada: '{guia.titulo}' (ID: {guia.id})")
        print(f"   Asignatura: {guia.asignatura.nombre}")
        print(f"   Carrera: {guia.carrera.get_nombre_display()}")
        
    except GuiaGenerada.DoesNotExist:
        print("\n❌ No se encontraron guías en la base de datos")
        return
    
    # Intentar generar el documento
    print("\n🔄 Generando documento Word...")
    try:
        word_buffer = generar_documento_word(guia)
        
        if word_buffer is None:
            print("❌ La función retornó None - revisa los logs arriba para ver el error")
            return
        
        # Verificar el tamaño del buffer
        buffer_size = word_buffer.getbuffer().nbytes
        print(f"✅ Documento generado exitosamente")
        print(f"   Tamaño: {buffer_size:,} bytes ({buffer_size / 1024:.2f} KB)")
        
        # Guardar el archivo de prueba
        test_file = os.path.join(os.path.dirname(__file__), 'test_output.docx')
        with open(test_file, 'wb') as f:
            f.write(word_buffer.getvalue())
        
        print(f"\n💾 Archivo de prueba guardado en: {test_file}")
        print("\n📋 Intenta abrir este archivo en Word para verificar si funciona")
        
        # Verificar que sea un archivo ZIP válido (los .docx son archivos ZIP)
        import zipfile
        try:
            with zipfile.ZipFile(test_file, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                print(f"\n✅ El archivo .docx es un ZIP válido con {len(file_list)} archivos internos")
                print("   Principales archivos:")
                for fname in file_list[:10]:
                    print(f"   - {fname}")
        except zipfile.BadZipFile:
            print("\n❌ ERROR: El archivo .docx NO es un ZIP válido")
            print("   Esto indica que el documento está corrupto")
        
    except Exception as e:
        print(f"\n❌ Error durante la generación:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_word_generation()
