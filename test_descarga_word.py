#!/usr/bin/env python
"""
Script para probar la descarga de archivos Word
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from guias.models import GuiaGenerada
import shutil

def test_descarga():
    """Simula la descarga de un archivo Word"""
    
    print("=" * 80)
    print("TEST DE DESCARGA DE ARCHIVO WORD")
    print("=" * 80)
    
    # Obtener la guía
    try:
        guia = GuiaGenerada.objects.latest('created_at')
        print(f"\n✅ Guía: '{guia.titulo}' (ID: {guia.id})")
    except GuiaGenerada.DoesNotExist:
        print("\n❌ No se encontraron guías")
        return
    
    if not guia.archivo_word:
        print("❌ La guía no tiene archivo Word")
        return
    
    print(f"   Archivo: {guia.archivo_word.name}")
    print(f"   Path: {guia.archivo_word.path}")
    
    # Verificar que el archivo existe
    if not os.path.exists(guia.archivo_word.path):
        print("\n❌ El archivo no existe en el disco")
        return
    
    # Verificar tamaño
    size = os.path.getsize(guia.archivo_word.path)
    print(f"   Tamaño: {size:,} bytes ({size/1024:.2f} KB)")
    
    # Verificar que sea un ZIP válido
    import zipfile
    try:
        with zipfile.ZipFile(guia.archivo_word.path, 'r') as zip_ref:
            files = zip_ref.namelist()
            print(f"   ✅ ZIP válido con {len(files)} componentes")
    except zipfile.BadZipFile:
        print("   ❌ El archivo está corrupto (no es un ZIP válido)")
        return
    
    # Copiar el archivo a un lugar de fácil acceso para prueba
    test_download = os.path.join(os.path.dirname(__file__), 'test_descarga.docx')
    shutil.copy2(guia.archivo_word.path, test_download)
    print(f"\n✅ Archivo copiado para prueba: {test_download}")
    
    # Simular lectura como lo haría la vista
    print("\n🔄 Simulando descarga HTTP...")
    try:
        with open(guia.archivo_word.path, 'rb') as f:
            content = f.read()
        
        print(f"   ✅ Archivo leído correctamente: {len(content):,} bytes")
        
        # Verificar que el contenido sea un ZIP válido
        from io import BytesIO
        import zipfile
        try:
            with zipfile.ZipFile(BytesIO(content), 'r') as zip_ref:
                print(f"   ✅ Contenido es un ZIP válido")
        except zipfile.BadZipFile:
            print("   ❌ El contenido leído está corrupto")
            
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")
    
    print("\n" + "=" * 80)
    print("CONCLUSIÓN:")
    print("Si ves todos ✅ arriba, el archivo debería descargarse correctamente.")
    print(f"Intenta abrir manualmente: {test_download}")
    print("=" * 80)

if __name__ == '__main__':
    test_descarga()
