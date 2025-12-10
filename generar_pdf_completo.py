import os, sys, django

sys.path.insert(0, '/Users/alvaroencinas/Desktop/centralizacion_laboratorios')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'centralizacion.settings')
django.setup()

from django.test import RequestFactory
from usuarios.models import Usuario as User
from guias.views import generar_practica_word

print("=" * 80)
print("GENERANDO PDF COMPLETO CON TODOS LOS DATOS")
print("=" * 80)

factory = RequestFactory()
user = User.objects.filter(is_superuser=True).first()
request = factory.get('/guias/practica/38/generar-word/')
request.user = user

print("\n🔄 Generando PDF de práctica ID 38...")
response = generar_practica_word(request, 38)

if response.status_code == 200:
    output_path = '/Users/alvaroencinas/Desktop/PRACTICA_COMPLETA_TODOS_CAMPOS.pdf'
    with open(output_path, 'wb') as f:
        f.write(response.content)
    
    print(f"\n✅ PDF GENERADO EXITOSAMENTE")
    print(f"   📁 Ubicación: {output_path}")
    print(f"   📊 Tamaño: {len(response.content):,} bytes ({len(response.content)/1024:.1f} KB)")
    print(f"\n" + "=" * 80)
    print("VERIFICAR QUE EL PDF CONTIENE:")
    print("=" * 80)
    print("  ✓ Datos Generales (Carrera, Semestre, Asignatura, etc.)")
    print("  ✓ Bibliografía (en tabla de Datos Generales)")
    print("  ✓ Competencias (4 registros)")
    print("  ✓ Criterios de Desempeño (4 - tipo='desempeno')")
    print("  ✓ Objetivos de la Práctica (3 - general, específico, aprendizaje)")
    print("  ✓ Fundamento Teórico (2 fundamentos)")
    print("  ✓ Materiales/Equipos/Herramientas/Reactivos (2 registros)")
    print("  ✓ Procedimientos (4 pasos detallados)")
    print("  ✓ Cálculos y Resultados (1 fórmula)")
    print("  ✓ Cuestionario (1 pregunta)")
    print("=" * 80)
    
    # Abrir automáticamente
    os.system(f'open "{output_path}"')
else:
    print(f"❌ Error: {response.status_code}")
    if hasattr(response, 'content'):
        print(response.content[:500])
