import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Verificar estructura de archivos estáticos
static_dir = BASE_DIR / 'static'
images_dir = static_dir / 'images'

print("=== VERIFICACIÓN DE ARCHIVOS ESTÁTICOS ===")
print(f"Base DIR: {BASE_DIR}")
print(f"Static DIR: {static_dir}")
print(f"Images DIR: {images_dir}")

print(f"\nStatic dir exists: {static_dir.exists()}")
print(f"Images dir exists: {images_dir.exists()}")

if images_dir.exists():
    print(f"\nArchivos en images/:")
    for file in images_dir.iterdir():
        print(f"  - {file.name} ({file.stat().st_size} bytes)")
else:
    print("\nERROR: La carpeta images/ no existe")

# Verificar permisos
try:
    print(f"\nPermisos de static/: {oct(static_dir.stat().st_mode)}")
    if images_dir.exists():
        print(f"Permisos de images/: {oct(images_dir.stat().st_mode)}")
except Exception as e:
    print(f"Error verificando permisos: {e}")