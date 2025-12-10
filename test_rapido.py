import os, sys, django

sys.path.insert(0, '/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import RequestFactory
from usuarios.models import Usuario as User
from guias.views import generar_practica_word

print("🔄 Generando PDF actualizado...")

factory = RequestFactory()
user = User.objects.filter(is_superuser=True).first()
request = factory.get('/guias/practica/38/generar-word/')
request.user = user

response = generar_practica_word(request, 38)

if response.status_code == 200:
    output_path = '/Users/alvaroencinas/Desktop/test_practica_38_CORREGIDO.pdf'
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ PDF generado: {output_path}")
    print(f"   Tamaño: {len(response.content):,} bytes")
    
    # Abrir automáticamente
    os.system(f'open "{output_path}"')
else:
    print(f"❌ Error: {response.status_code}")
