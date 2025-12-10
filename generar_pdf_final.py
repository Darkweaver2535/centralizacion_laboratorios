#!/usr/bin/env python
import os, sys, django

sys.path.insert(0, '/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import RequestFactory
from usuarios.models import Usuario as User
from guias.views import generar_practica_word

print("Generando PDF con todas las correcciones aplicadas...")
print("=" * 70)

factory = RequestFactory()
user = User.objects.filter(is_superuser=True).first()
request = factory.get('/guias/practica/38/generar-word/')
request.user = user

response = generar_practica_word(request, 38)

if response.status_code == 200:
    output_path = '/Users/alvaroencinas/Desktop/PRACTICA_FINAL_CORREGIDA.pdf'
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"✅ PDF generado exitosamente")
    print(f"📄 Ubicación: {output_path}")
    print(f"📊 Tamaño: {len(response.content):,} bytes")
    print("\n" + "=" * 70)
    print("VERIFICAR EN EL PDF:")
    print("=" * 70)
    print("✅ Asignatura: QUÍMICA ORGÁNICA (mayúsculas)")
    print("✅ Sin color emigris en encabezados")
    print("✅ Contenido Analítico: FACTOR DE COMPRESIBILIDAD")
    print("✅ Unidad Didáctica: PROPIEDADES EMPIRICAS DE LOS GASES IDEALES")
    print("✅ Competencias: (datos del formulario)")
    print("✅ Criterios de Desempeño: Analiza las leyes y ecuaciones...")
    print("✅ Objetivo de la Práctica: OBJETIVO DE LA PRACTICA")
    print("✅ Fundamento Teórico: SIN numeración 5.1")
    print("✅ Procedimiento: SIN '1. Procedimiento 1'")
    print("✅ Cálculos: SIN '8.1. Cálculo 1'")
    print("✅ Cuestionario: SIN numeración '1.'")
    print("=" * 70)
    
    import subprocess
    subprocess.run(['open', output_path])
else:
    print(f"❌ Error: {response.status_code}")
