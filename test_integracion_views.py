"""
Script para probar la generación de PDF con LaTeX desde Django views
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import RequestFactory
from usuarios.models import Usuario as User
from guias.views import generar_practica_word

# Crear un request falso
factory = RequestFactory()

# Usar el primer usuario admin disponible
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.filter(is_staff=True).first()
if not user:
    user = User.objects.first()

if not user:
    print("ERROR: No hay usuarios en la base de datos")
    sys.exit(1)

print(f"Usando usuario existente: {user.username}")

# Crear request
request = factory.get('/guias/practica/38/generar-word/')
request.user = user

print("=" * 60)
print("PROBANDO GENERACIÓN DE PDF CON LaTeX")
print("=" * 60)
print()

try:
    # Llamar a la función
    response = generar_practica_word(request, 38)
    
    print(f"\n✅ Respuesta recibida")
    print(f"   Content-Type: {response.get('Content-Type', 'N/A')}")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content_length = len(response.content)
        print(f"   Tamaño del archivo: {content_length:,} bytes ({content_length/1024:.2f} KB)")
        
        # Guardar el PDF para verificación
        output_path = '/Users/alvaroencinas/Desktop/test_practica_38.pdf'
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"\n📄 PDF guardado en: {output_path}")
        print(f"\n✅ ¡PRUEBA EXITOSA! La integración funciona correctamente.")
        print(f"\nPuedes abrir el archivo con: open {output_path}")
        
    else:
        print(f"\n❌ Error: Código de estado {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   Contenido: {response.content[:500]}")
            
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
